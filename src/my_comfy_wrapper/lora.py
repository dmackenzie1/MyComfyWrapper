from __future__ import annotations

from pathlib import Path

from .domain.lora import LoraCatalog, LoraEntry


def parse_lora_csv(path: Path) -> list[LoraEntry]:
    return LoraCatalog.from_csv(path).entries


def select_enabled_loras(entries: list[LoraEntry]) -> list[LoraEntry]:
    return [entry for entry in entries if entry.enabled]
