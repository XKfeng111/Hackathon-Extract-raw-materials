# Flask JSONL Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Flask demo that uploads raw materials, generates draft structured JSONL records, previews them in the browser, and downloads generated outputs.

**Architecture:** The Flask app owns routes, validation, output persistence, and template rendering. Focused `raw_materials` modules handle text extraction, chunking, and JSONL record generation so the web layer stays small and testable.

**Tech Stack:** Python 3.11+, Flask, python-docx, pypdf, pytest.

---

## File Structure

- Create `requirements.txt` — runtime/test dependencies.
- Create `app.py` — Flask routes for upload, preview, and downloads.
- Create `raw_materials/__init__.py` — package marker.
- Create `raw_materials/reader.py` — extract text from `.pdf`, `.docx`, `.txt`, `.md`.
- Create `raw_materials/chunker.py` — split normalized text into generation chunks.
- Create `raw_materials/jsonl_builder.py` — build draft records and serialize outputs.
- Create `templates/index.html` — upload form, source type choices, inline preview, download links.
- Create `static/style.css` — simple demo styling.
- Create `outputs/.gitkeep` — keep output directory in repo while ignoring generated files.
- Create `tests/test_reader_builder.py` — unit tests for reader/chunker/builder.
- Create `tests/test_app.py` — Flask route tests.
- Modify `README.md` — setup and run instructions.

## Tasks

### Task 1: Project dependencies and unit tests

**Files:**
- Create: `requirements.txt`
- Create: `tests/test_reader_builder.py`

- [ ] **Step 1: Add failing unit tests**

Write tests that import `raw_materials.reader`, `raw_materials.chunker`, and `raw_materials.jsonl_builder`; they should fail because those modules do not exist yet.

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_reader_builder.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'raw_materials'`.

- [ ] **Step 3: Add dependencies**

Add Flask, python-docx, pypdf, and pytest to `requirements.txt`.

### Task 2: Reader, chunker, and builder

**Files:**
- Create: `raw_materials/__init__.py`
- Create: `raw_materials/reader.py`
- Create: `raw_materials/chunker.py`
- Create: `raw_materials/jsonl_builder.py`

- [ ] **Step 1: Implement reader**

Provide `extract_text_from_upload(file_bytes: bytes, filename: str) -> str` and `is_supported_filename(filename: str) -> bool`.

- [ ] **Step 2: Implement chunker**

Provide `chunk_text(text: str, source_type: str) -> list[str]`.

- [ ] **Step 3: Implement builder**

Provide `build_records(...)`, `records_to_jsonl(...)`, `records_to_pretty_json(...)`, and `records_to_preview_markdown(...)`.

- [ ] **Step 4: Run unit tests**

Run: `python -m pytest tests/test_reader_builder.py -q`
Expected: PASS.

### Task 3: Flask app route tests

**Files:**
- Create: `tests/test_app.py`

- [ ] **Step 1: Add failing Flask tests**

Write tests for home page source type choices, TXT upload preview generation, JSONL download, invalid source type, and unsupported file extension.

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_app.py -q`
Expected: FAIL because `app.py` and templates do not exist yet.

### Task 4: Flask app, template, and styling

**Files:**
- Create: `app.py`
- Create: `templates/index.html`
- Create: `static/style.css`
- Create: `outputs/.gitkeep`

- [ ] **Step 1: Implement Flask routes**

Implement `GET /`, `POST /generate`, and `GET /download/<run_id>/<kind>`.

- [ ] **Step 2: Implement page template**

Render upload form, exact three source type choices, inline preview cards, and download links.

- [ ] **Step 3: Add styling**

Create a clean single-page demo layout.

- [ ] **Step 4: Run Flask tests**

Run: `python -m pytest tests/test_app.py -q`
Expected: PASS.

### Task 5: README, full verification, and publish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README**

Document setup, running the app, upload workflow, source types, output files, and draft/human-review caveat.

- [ ] **Step 2: Run all tests**

Run: `python -m pytest -q`
Expected: all tests pass.

- [ ] **Step 3: Commit implementation**

Commit all feature files with a clear message.

- [ ] **Step 4: Merge to main and push**

Merge the feature branch into `main` and push to `origin/main`.

## Self-Review

- Spec coverage: upload, three source types, extraction, browser preview, and downloads are covered by Tasks 1-5.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: function names in the plan match the intended module APIs.
