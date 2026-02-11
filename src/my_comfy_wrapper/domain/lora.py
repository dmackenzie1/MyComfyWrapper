from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoraEntry:
    name_or_path: str
    weight: float
    trigger_words: str
    enabled: bool


REQUIRED_COLUMNS = {"name_or_path", "weight", "trigger_words", "enabled"}


class LoraCatalog:
    def __init__(self, entries: list[LoraEntry]) -> None:
        self.entries = entries

    @classmethod
    def from_csv(cls, path: Path) -> "LoraCatalog":
        if not path.exists():
            raise FileNotFoundError(f"LoRA CSV not found: {path}")

        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("LoRA CSV is empty.")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(f"LoRA CSV missing columns: {sorted(missing)}")

            entries: list[LoraEntry] = []
            for idx, row in enumerate(reader, start=2):
                try:
                    weight = float(row["weight"])
                except ValueError as exc:
                    raise ValueError(f"Invalid weight at row {idx}: {row['weight']}") from exc

                enabled = str(row["enabled"]).strip().lower() in {"1", "true", "yes", "on"}
                entries.append(
                    LoraEntry(
                        name_or_path=row["name_or_path"].strip(),
                        weight=weight,
                        trigger_words=row["trigger_words"].strip(),
                        enabled=enabled,
                    )
                )

        return cls(entries)

    def enabled(self) -> list[LoraEntry]:
        return [entry for entry in self.entries if entry.enabled]

    def enabled_trigger_words(self) -> list[str]:
        words: list[str] = []
        for entry in self.enabled():
            if entry.trigger_words:
                words.append(entry.trigger_words)
        return words
