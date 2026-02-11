from pathlib import Path

from my_comfy_wrapper.lora import parse_lora_csv, select_enabled_loras


def test_lora_csv_parsing_and_enabled_selection(tmp_path: Path):
    csv_path = tmp_path / "loras.csv"
    csv_path.write_text(
        "name_or_path,weight,trigger_words,enabled\n"
        "a.safetensors,1.0,cinematic,true\n"
        "b.safetensors,0.5,smooth,false\n",
        encoding="utf-8",
    )

    parsed = parse_lora_csv(csv_path)
    assert len(parsed) == 2
    enabled = select_enabled_loras(parsed)
    assert len(enabled) == 1
    assert enabled[0].name_or_path == "a.safetensors"
