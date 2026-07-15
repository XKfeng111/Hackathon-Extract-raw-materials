import json

from raw_materials.chunker import chunk_text
from raw_materials.jsonl_builder import (
    build_records,
    default_mentor_mode,
    records_to_jsonl,
    records_to_preview_markdown,
    records_to_pretty_json,
)
from raw_materials.reader import extract_text_from_upload, is_supported_filename


def test_supported_filename_accepts_expected_raw_material_types():
    assert is_supported_filename("proposal.pdf")
    assert is_supported_filename("feedback.docx")
    assert is_supported_filename("notes.txt")
    assert is_supported_filename("summary.md")
    assert not is_supported_filename("spreadsheet.xlsx")


def test_extract_text_from_txt_bytes_normalizes_text():
    text = extract_text_from_upload(b"Line one\r\n\r\nLine two", "notes.txt")
    assert text == "Line one\n\nLine two"


def test_chunk_text_splits_numbered_feedback_items():
    chunks = chunk_text(
        "1. Add a clearer motivation paragraph.\n"
        "2. Revise Figure 2 to show the control experiment.\n",
        "Papers_Proposal",
    )
    assert chunks == [
        "Add a clearer motivation paragraph.",
        "Revise Figure 2 to show the control experiment.",
    ]


def test_default_mentor_mode_maps_three_source_types():
    assert default_mentor_mode("Papers_Proposal") == "research_problem_feedback"
    assert default_mentor_mode("Research_Meeting_Minutes") == "research_problem_feedback"
    assert default_mentor_mode("Talk_Presentation_Slides") == "presentation_feedback"


def test_build_records_marks_every_record_as_draft_needing_human_review():
    records = build_records(
        chunks=["Add more evidence for the claim.", "Clarify the next experiment."],
        project_name="WVTR",
        source_type="Research_Meeting_Minutes",
        source_date="2026-07-15",
        source_file="meeting.txt",
        mentor_mode="research_problem_feedback",
    )
    assert len(records) == 2
    assert records[0]["project_name"] == "WVTR"
    assert records[0]["source_type"] == "Research_Meeting_Minutes"
    assert records[0]["metadata"]["verified_by_human"] is False
    assert records[0]["metadata"]["confidence"] == "draft"
    assert "needs_review" in records[0]["tags"]
    assert records[0]["training_output"]["action_items"]


def test_serializers_create_jsonl_pretty_json_and_markdown_preview():
    records = build_records(
        chunks=["Revise the slide title to state the conclusion."],
        project_name="Talk Demo",
        source_type="Talk_Presentation_Slides",
        source_date="",
        source_file="talk.md",
        mentor_mode="presentation_feedback",
    )

    jsonl = records_to_jsonl(records)
    parsed_line = json.loads(jsonl.strip())
    assert parsed_line["source_file"] == "talk.md"

    pretty = records_to_pretty_json(records)
    assert json.loads(pretty)[0]["mentor_mode"] == "presentation_feedback"

    preview = records_to_preview_markdown(records)
    assert "# Draft JSONL Preview" in preview
    assert "Talk Demo" in preview
    assert "verified_by_human: false" in preview
