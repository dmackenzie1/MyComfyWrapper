from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..http_utils import http_get_bytes, http_get_json, http_post_json


class ComfyApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def submit_prompt(self, prompt_graph: dict[str, Any]) -> dict[str, Any]:
        return http_post_json(f"{self.base_url}/prompt", {"prompt": prompt_graph})

    def wait_for_completion(self, prompt_id: str, timeout_s: int = 3600) -> dict[str, Any]:
        start = time.time()
        while True:
            history = http_get_json(f"{self.base_url}/history/{prompt_id}")
            entry = history.get(prompt_id) if history else None
            if entry:
                return entry
            if time.time() - start > timeout_s:
                raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")
            time.sleep(2)

    def download_outputs(self, history_entry: dict[str, Any], destination_dir: Path) -> list[str]:
        destination_dir.mkdir(parents=True, exist_ok=True)
        downloaded: list[str] = []

        outputs = history_entry.get("outputs", {})
        for _, output in outputs.items():
            files = output.get("images", []) + output.get("gifs", []) + output.get("videos", [])
            for file_info in files:
                filename = file_info.get("filename")
                if not filename:
                    continue
                content = http_get_bytes(
                    f"{self.base_url}/view",
                    {
                        "filename": filename,
                        "subfolder": file_info.get("subfolder", ""),
                        "type": file_info.get("type", "output"),
                    },
                )
                out_path = destination_dir / filename
                out_path.write_bytes(content)
                downloaded.append(str(out_path))

        return downloaded


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
