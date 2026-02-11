from pathlib import Path

from my_comfy_wrapper.workflow import WorkflowTemplate
from my_comfy_wrapper.lora import LoraEntry


def test_workflow_patch_updates_prompts_and_loras_and_seed():
    template = WorkflowTemplate.from_path(Path("wrappers/20260211-wan2-template.json"))
    patched = template.patch(
        image_path=Path("inputs/example.png"),
        positive_prompt="a cinematic drone shot over mountains",
        negative_prompt="blurry, low quality",
        loras=[
            LoraEntry("high/a.safetensors", 0.9, "", True),
            LoraEntry("low/b.safetensors", 0.8, "", True),
        ],
        seed=12345,
        output_prefix="sample/prefix",
    )

    by_id = {node["id"]: node for node in patched.nodes}

    assert by_id[6]["widgets_values"][0] == "a cinematic drone shot over mountains"
    assert by_id[7]["widgets_values"][0] == "blurry, low quality"
    assert by_id[67]["widgets_values"][0] == "high/a.safetensors"
    assert by_id[67]["widgets_values"][1] == 0.9
    assert by_id[68]["widgets_values"][0] == "low/b.safetensors"
    assert by_id[57]["widgets_values"][1] == 12345
