from __future__ import annotations

import base64
from pathlib import Path
from urllib.error import URLError

from ..http_utils import http_post_json


class OllamaClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def generate_text(self, model: str, prompt: str) -> str:
        response = http_post_json(
            f"{self.base_url}/api/generate",
            {"model": model, "prompt": prompt, "stream": False},
        )
        return str(response.get("response", ""))

    def generate_with_image(self, model: str, prompt: str, image_path: Path) -> str:
        image_data = base64.b64encode(image_path.read_bytes()).decode("ascii")
        response = http_post_json(
            f"{self.base_url}/api/generate",
            {"model": model, "prompt": prompt, "images": [image_data], "stream": False},
        )
        return str(response.get("response", ""))


__all__ = ["OllamaClient", "URLError"]
