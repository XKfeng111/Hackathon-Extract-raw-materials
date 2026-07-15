from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from flask import Flask, Response, abort, render_template, request, send_file
from werkzeug.utils import secure_filename

from raw_materials.chunker import chunk_text
from raw_materials.jsonl_builder import (
    SOURCE_TYPE_TO_MENTOR_MODE,
    build_records,
    default_mentor_mode,
    records_to_jsonl,
    records_to_preview_markdown,
    records_to_pretty_json,
    slugify,
)
from raw_materials.reader import SUPPORTED_EXTENSIONS, extract_text_from_upload, is_supported_filename


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
app.config["OUTPUT_DIR"] = Path(__file__).parent / "outputs"

DOWNLOAD_FILENAMES = {
    "jsonl": "records.jsonl",
    "json": "records_pretty.json",
    "md": "preview.md",
}


def get_output_dir() -> Path:
    return Path(app.config["OUTPUT_DIR"])


def render_home(**context: Any):
    defaults = {
        "error": "",
        "records": [],
        "record_count": 0,
        "run_id": "",
        "download_urls": {},
        "form": {
            "project_name": "",
            "source_type": "Research_Meeting_Minutes",
            "source_date": "",
            "mentor_mode": "",
        },
    }
    defaults.update(context)
    return render_template(
        "index.html",
        source_types=SOURCE_TYPE_TO_MENTOR_MODE,
        supported_extensions=", ".join(sorted(SUPPORTED_EXTENSIONS)),
        **defaults,
    )


@app.get("/")
def home():
    return render_home()


@app.post("/generate")
def generate():
    form = {
        "project_name": request.form.get("project_name", "").strip(),
        "source_type": request.form.get("source_type", "").strip(),
        "source_date": request.form.get("source_date", "").strip(),
        "mentor_mode": request.form.get("mentor_mode", "").strip(),
    }
    uploaded_file = request.files.get("file")

    if not form["project_name"]:
        return render_home(error="Project name is required.", form=form), 400

    if form["source_type"] not in SOURCE_TYPE_TO_MENTOR_MODE:
        return render_home(error="Choose one of the three source types.", form=form), 400

    if not form["mentor_mode"]:
        form["mentor_mode"] = default_mentor_mode(form["source_type"])

    if not uploaded_file or not uploaded_file.filename:
        return render_home(error="Please choose a raw material file.", form=form), 400

    filename = secure_filename(uploaded_file.filename) or Path(uploaded_file.filename).name
    if not is_supported_filename(filename):
        return render_home(
            error=f"Unsupported file type. Use one of: {', '.join(sorted(SUPPORTED_EXTENSIONS))}.",
            form=form,
        ), 400

    try:
        file_bytes = uploaded_file.read()
        text = extract_text_from_upload(file_bytes, filename)
        chunks = chunk_text(text, form["source_type"])
        if not chunks:
            raise ValueError("No usable chunks were generated from this file.")
        records = build_records(
            chunks=chunks,
            project_name=form["project_name"],
            source_type=form["source_type"],
            source_date=form["source_date"],
            source_file=filename,
            mentor_mode=form["mentor_mode"],
        )
    except ValueError as exc:
        return render_home(error=str(exc), form=form), 400

    run_id = save_outputs(records, form["project_name"], form["source_type"])
    response = Response(
        render_home(
            records=records,
            record_count=len(records),
            run_id=run_id,
            download_urls={
                "jsonl": f"/download/{run_id}/jsonl",
                "json": f"/download/{run_id}/json",
                "md": f"/download/{run_id}/md",
            },
            form=form,
        )
    )
    response.headers["X-Run-Id"] = run_id
    return response


def save_outputs(records: list[dict], project_name: str, source_type: str) -> str:
    run_id = f"{slugify(project_name, 4)}_{slugify(source_type, 4)}_{secrets.token_hex(4)}"
    run_dir = get_output_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / DOWNLOAD_FILENAMES["jsonl"]).write_text(records_to_jsonl(records), encoding="utf-8")
    (run_dir / DOWNLOAD_FILENAMES["json"]).write_text(records_to_pretty_json(records), encoding="utf-8")
    (run_dir / DOWNLOAD_FILENAMES["md"]).write_text(records_to_preview_markdown(records), encoding="utf-8")
    return run_id


@app.get("/download/<run_id>/<kind>")
def download(run_id: str, kind: str):
    if kind not in DOWNLOAD_FILENAMES:
        abort(404)
    safe_run_id = secure_filename(run_id)
    if safe_run_id != run_id:
        abort(404)

    path = get_output_dir() / run_id / DOWNLOAD_FILENAMES[kind]
    if not path.exists():
        abort(404)

    mimetypes = {
        "jsonl": "application/jsonl; charset=utf-8",
        "json": "application/json; charset=utf-8",
        "md": "text/markdown; charset=utf-8",
    }
    return send_file(
        path,
        mimetype=mimetypes[kind],
        as_attachment=True,
        download_name=DOWNLOAD_FILENAMES[kind],
    )


@app.errorhandler(413)
def file_too_large(_error: Exception):
    return render_home(error="The file is too large. Maximum upload size is 20 MB."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
