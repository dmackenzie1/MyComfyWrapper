from __future__ import annotations

import json

from ..domain.lora import LoraEntry
from .ollama_client import OllamaClient, URLError


class PromptService:
    def __init__(self, ollama: OllamaClient, model: str) -> None:
        self.ollama = ollama
        self.model = model

    def generate_prompts(
        self,
        description: str,
        loras: list[LoraEntry],
        action_hint: str,
    ) -> tuple[str, str, dict[str, str]]:
        positive, negative, first_raw = self._first_pass(description)
        refined_positive, refined_negative, second_raw = self._second_pass(
            positive_prompt=positive,
            negative_prompt=negative,
            loras=loras,
            action_hint=action_hint,
        )

        metadata = {
            "first_pass": first_raw,
            "second_pass": second_raw,
        }
        return refined_positive, refined_negative, metadata

    def _first_pass(self, description: str) -> tuple[str, str, str]:
        instruction = (
            "Create JSON with keys positive_prompt and negative_prompt for image-to-video generation. "
            f"Description: {description}"
        )
        fallback_positive = f"cinematic video scenario of {description}"
        fallback_negative = "blurry, low quality, artifacts, watermark"

        try:
            raw = self.ollama.generate_text(self.model, instruction)
            parsed = json.loads(raw)
            return (
                str(parsed.get("positive_prompt", fallback_positive)),
                str(parsed.get("negative_prompt", fallback_negative)),
                raw,
            )
        except (URLError, json.JSONDecodeError):
            return fallback_positive, fallback_negative, "FIRST_PASS_FALLBACK"

    def _second_pass(
        self,
        positive_prompt: str,
        negative_prompt: str,
        loras: list[LoraEntry],
        action_hint: str,
    ) -> tuple[str, str, str]:
        lora_words = [entry.trigger_words for entry in loras if entry.trigger_words]
        lora_words_text = "; ".join(lora_words) if lora_words else "none"
        action_text = action_hint or "natural cinematic motion"

        instruction = (
            "Refine prompts for image-to-video generation. "
            "Return JSON with keys positive_prompt and negative_prompt. "
            "Keep prompts concise. "
            f"Current positive prompt: {positive_prompt}\n"
            f"Current negative prompt: {negative_prompt}\n"
            f"Required LoRA trigger words: {lora_words_text}\n"
            f"Desired action: {action_text}"
        )

        try:
            raw = self.ollama.generate_text(self.model, instruction)
            parsed = json.loads(raw)
            return (
                str(parsed.get("positive_prompt", positive_prompt)),
                str(parsed.get("negative_prompt", negative_prompt)),
                raw,
            )
        except (URLError, json.JSONDecodeError):
            suffix = f" {', '.join(lora_words)}" if lora_words else ""
            return (
                f"{positive_prompt}. action: {action_text}.{suffix}".strip(),
                negative_prompt,
                "SECOND_PASS_FALLBACK",
            )
