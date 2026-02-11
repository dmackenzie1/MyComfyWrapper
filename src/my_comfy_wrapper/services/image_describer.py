from __future__ import annotations

import json
from pathlib import Path

from .ollama_client import OllamaClient, URLError


class ImageDescriber:
    def __init__(self, ollama: OllamaClient, vision_enabled: bool, vision_model: str | None) -> None:
        self.ollama = ollama
        self.vision_enabled = vision_enabled
        self.vision_model = vision_model

    def describe(self, image_path: Path) -> tuple[str, str]:
        basic = self.describe_basic(image_path)

        if not self.vision_enabled or not self.vision_model:
            return basic, "basic"

        prompt = (
            "Describe this image for image-to-video generation in one short paragraph. "
            "Focus on subject, environment, camera framing, and motion cues."
        )
        try:
            vision_description = self.ollama.generate_with_image(self.vision_model, prompt, image_path).strip()
            if vision_description:
                return vision_description, "vision"
        except URLError:
            pass

        return basic, "basic_fallback"

    def describe_basic(self, image_path: Path) -> str:
        stem = image_path.stem.replace("_", " ").replace("-", " ")
        parts = [f"Image based on file name: {stem}"]

        txt_sidecar = image_path.with_suffix(".txt")
        json_sidecar = image_path.with_suffix(".json")
        if txt_sidecar.exists():
            parts.append(f"Sidecar: {txt_sidecar.read_text(encoding='utf-8').strip()}")
        elif json_sidecar.exists():
            data = json.loads(json_sidecar.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key in ("description", "caption", "title"):
                    if key in data and data[key]:
                        parts.append(f"{key}: {data[key]}")
                        break

        return ". ".join(part for part in parts if part)
