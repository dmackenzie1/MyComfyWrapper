from __future__ import annotations

import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from ..config import AppConfig
from ..domain.lora import LoraCatalog
from ..services.comfy_api import ComfyApiClient, write_json
from ..services.image_describer import ImageDescriber
from ..services.ollama_client import OllamaClient
from ..services.prompt_service import PromptService
from ..workflow import WorkflowTemplate

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class PipelineApp:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.template = WorkflowTemplate.from_path(config.workflow_template)
        self.lora_catalog = LoraCatalog.from_csv(config.lora_csv)

        ollama = OllamaClient(config.ollama_base_url)
        self.describer = ImageDescriber(
            ollama=ollama,
            vision_enabled=config.enable_vision,
            vision_model=config.ollama_vision_model,
        )
        self.prompt_service = PromptService(ollama=ollama, model=config.ollama_model)
        self.comfy_api = ComfyApiClient(config.comfy_base_url)

    def inspect_workflow(self) -> list[str]:
        reports = self.template.inspect(self.config.workflow_node_overrides)
        lines = []
        for report in reports:
            lines.append(
                f"{report.target_name}: candidates={report.candidates} selected={report.selected} method={report.method}"
            )
            if report.warning:
                lines.append(f"  warning: {report.warning}")
        return lines

    def run(self) -> None:
        images = [p for p in sorted(self.config.input_dir.iterdir()) if p.suffix.lower() in IMAGE_EXTS]
        if not images:
            raise ValueError(f"No images found in {self.config.input_dir}")

        with ThreadPoolExecutor(max_workers=max(1, self.config.concurrency)) as executor:
            futures = []
            for image in images:
                for variant in range(1, self.config.variants + 1):
                    futures.append(executor.submit(self._run_single_variant, image, variant))
            for future in futures:
                future.result()

    def _run_single_variant(self, image_path: Path, variant: int) -> None:
        image_id = image_path.stem
        variant_dir = self.config.output_dir / image_id / f"variant_{variant}"
        manifest_path = variant_dir / "manifest.json"

        if self.config.resume and manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("status") == "completed":
                print(f"[resume] Skipping {image_id} variant {variant}")
                return

        enabled_loras = self.lora_catalog.enabled()
        seed = self._pick_seed(variant)
        description, description_mode = self.describer.describe(image_path)
        positive_prompt, negative_prompt, prompt_meta = self.prompt_service.generate_prompts(
            description=description,
            loras=enabled_loras,
            action_hint=self.config.action_hint,
        )

        output_prefix = f"{image_id}/variant_{variant}/result"
        patched = self.template.patch(
            image_path=image_path,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            loras=enabled_loras,
            seed=seed,
            output_prefix=output_prefix,
            overrides=self.config.workflow_node_overrides,
        )

        variant_dir.mkdir(parents=True, exist_ok=True)
        write_json(variant_dir / "patched_workflow.json", patched.to_dict())
        write_json(
            variant_dir / "prompts.json",
            {
                "description": description,
                "description_mode": description_mode,
                "positive_prompt": positive_prompt,
                "negative_prompt": negative_prompt,
                "prompt_generation": prompt_meta,
                "action_hint": self.config.action_hint,
            },
        )
        write_json(variant_dir / "loras.json", [asdict(entry) for entry in enabled_loras])

        if self.config.dry_run:
            write_json(
                manifest_path,
                {
                    "status": "dry_run",
                    "image": str(image_path),
                    "variant": variant,
                    "seed": seed,
                },
            )
            print(f"[dry-run] {image_id} variant {variant}")
            return

        submitted_at = time.time()
        prompt_graph = patched.to_prompt_graph()
        write_json(variant_dir / "submission_payload.json", {"prompt": prompt_graph})

        submission = self.comfy_api.submit_prompt(prompt_graph)
        write_json(variant_dir / "submission_response.json", submission)

        prompt_id = submission.get("prompt_id")
        if not prompt_id:
            raise ValueError(f"Comfy submission missing prompt_id: {submission}")

        history_entry = self.comfy_api.wait_for_completion(prompt_id)
        write_json(variant_dir / "history_response.json", history_entry)
        files = self.comfy_api.download_outputs(history_entry, variant_dir / "files")

        write_json(
            manifest_path,
            {
                "status": "completed",
                "image": str(image_path),
                "variant": variant,
                "seed": seed,
                "prompt_id": prompt_id,
                "submitted_at": submitted_at,
                "completed_at": time.time(),
                "files": files,
            },
        )

    def _pick_seed(self, variant: int) -> int:
        if self.config.seed is not None and self.config.seed_strategy == "fixed":
            return self.config.seed
        if self.config.seed is not None and self.config.seed_strategy == "increment":
            return self.config.seed + variant - 1
        if self.config.seed is not None:
            return self.config.seed
        return random.randint(1, 2**31 - 1)
