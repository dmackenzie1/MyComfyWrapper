import pytest
from pathlib import Path

from my_comfy_wrapper.application.pipeline import PipelineApp
from my_comfy_wrapper.config import AppConfig
from my_comfy_wrapper.cli import make_parser


def test_inspect_workflow_does_not_require_lora_csv(tmp_path: Path):
    config = AppConfig(
        input_dir=tmp_path / "missing-inputs",
        workflow_template=Path("wrappers/20260211-wan2-template.json"),
        lora_csv=tmp_path / "missing-loras.csv",
        output_dir=tmp_path / "outputs",
        variants=1,
        seed=None,
        seed_strategy="random",
        comfy_base_url="http://127.0.0.1:8188",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="llama3.1:8b",
        ollama_vision_model=None,
        enable_vision=False,
        action_hint="",
        concurrency=1,
        resume=False,
        dry_run=True,
        workflow_node_overrides={},
    )

    app = PipelineApp(config)
    reports = app.inspect_workflow()

    assert reports
    assert any(line.startswith("positive_prompt:") for line in reports)


def test_inspect_workflow_rejects_dry_run_flag():
    parser = make_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([
            "inspect-workflow",
            "--workflow-template",
            "wrappers/20260211-wan2-template.json",
            "--dry-run",
        ])


def test_run_accepts_dry_run_flag():
    parser = make_parser()

    args = parser.parse_args([
        "run",
        "--workflow-template",
        "wrappers/20260211-wan2-template.json",
        "--dry-run",
    ])

    assert args.dry_run is True

def test_inspect_workflow_sets_dry_run_default_false():
    parser = make_parser()

    args = parser.parse_args([
        "inspect-workflow",
        "--workflow-template",
        "wrappers/20260211-wan2-template.json",
    ])

    assert args.dry_run is False

