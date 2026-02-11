from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .lora import LoraEntry


@dataclass
class InspectReport:
    target_name: str
    candidates: list[int]
    selected: int | None
    method: str
    warning: str | None = None


class WorkflowTemplate:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.nodes = data.get("nodes", [])

    @classmethod
    def from_path(cls, path: Path) -> "WorkflowTemplate":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def clone(self) -> "WorkflowTemplate":
        return WorkflowTemplate(copy.deepcopy(self.data))

    def _find_candidates(self, predicate) -> list[dict[str, Any]]:
        return [node for node in self.nodes if predicate(node)]

    @staticmethod
    def _set_widget_by_input_name(node: dict[str, Any], input_name: str, value: Any) -> bool:
        widget_inputs = [i for i in node.get("inputs", []) if i.get("widget")]
        for index, entry in enumerate(widget_inputs):
            if entry.get("name") == input_name:
                while len(node.setdefault("widgets_values", [])) <= index:
                    node["widgets_values"].append(None)
                node["widgets_values"][index] = value
                return True
        return False

    def inspect(self, overrides: dict[str, int] | None = None) -> list[InspectReport]:
        overrides = overrides or {}

        strategies = {
            "positive_prompt": lambda n: n.get("type") == "CLIPTextEncode" and "positive" in (n.get("title", "").lower()),
            "negative_prompt": lambda n: n.get("type") == "CLIPTextEncode" and "negative" in (n.get("title", "").lower()),
            "image_input": lambda n: "image" in n.get("type", "").lower() and any(i.get("widget") for i in n.get("inputs", [])),
            "save_prefix": lambda n: n.get("type") in {"SaveVideo", "SaveImage"},
            "sampler": lambda n: "Sampler" in n.get("type", ""),
            "lora": lambda n: n.get("type") == "LoraLoader",
        }

        reports: list[InspectReport] = []
        for key, matcher in strategies.items():
            candidates = sorted(node["id"] for node in self._find_candidates(matcher))
            selected = None
            method = "auto"
            warning = None
            if key in overrides:
                selected = overrides[key]
                method = "override"
            elif candidates:
                selected = candidates[0]
                if len(candidates) > 1 and key not in {"sampler", "lora"}:
                    warning = "Multiple candidates detected; first candidate selected."
            reports.append(InspectReport(key, candidates, selected, method, warning))

        return reports

    def patch(
        self,
        image_path: Path,
        positive_prompt: str,
        negative_prompt: str,
        loras: list[LoraEntry],
        seed: int,
        output_prefix: str,
        overrides: dict[str, int] | None = None,
    ) -> "WorkflowTemplate":
        patched = self.clone()
        reports = patched.inspect(overrides)
        by_key = {r.target_name: r for r in reports}

        node_map = {node["id"]: node for node in patched.nodes}

        if by_key["positive_prompt"].selected is not None:
            node = node_map[by_key["positive_prompt"].selected]
            patched._set_widget_by_input_name(node, "text", positive_prompt) or node.setdefault("widgets_values", [positive_prompt])
        if by_key["negative_prompt"].selected is not None:
            node = node_map[by_key["negative_prompt"].selected]
            patched._set_widget_by_input_name(node, "text", negative_prompt) or node.setdefault("widgets_values", [negative_prompt])
        if by_key["save_prefix"].selected is not None:
            node = node_map[by_key["save_prefix"].selected]
            patched._set_widget_by_input_name(node, "filename_prefix", output_prefix)

        # Image input patching best-effort for known widget names.
        image_target = by_key["image_input"].selected
        if image_target is not None:
            node = node_map[image_target]
            patched._set_widget_by_input_name(node, "image", str(image_path))
            patched._set_widget_by_input_name(node, "image_path", str(image_path))
            patched._set_widget_by_input_name(node, "filename", str(image_path))

        sampler_nodes = [node_map[node_id] for node_id in by_key["sampler"].candidates]
        for sampler in sampler_nodes:
            patched._set_widget_by_input_name(sampler, "noise_seed", seed)
            patched._set_widget_by_input_name(sampler, "seed", seed)

        lora_node_ids = by_key["lora"].candidates
        for idx, node_id in enumerate(lora_node_ids):
            node = node_map[node_id]
            if idx < len(loras):
                chosen = loras[idx]
                patched._set_widget_by_input_name(node, "lora_name", chosen.name_or_path)
                patched._set_widget_by_input_name(node, "strength_model", chosen.weight)
                patched._set_widget_by_input_name(node, "strength_clip", chosen.weight)

        return patched

    def to_dict(self) -> dict[str, Any]:
        return self.data

    def to_prompt_graph(self) -> dict[str, Any]:
        links = {link[0]: link for link in self.data.get("links", [])}
        graph: dict[str, Any] = {}

        for node in self.nodes:
            node_id = str(node["id"])
            graph[node_id] = {
                "class_type": node.get("type"),
                "inputs": {},
            }
            widget_inputs = [i for i in node.get("inputs", []) if i.get("widget")]
            for idx, input_def in enumerate(widget_inputs):
                if idx < len(node.get("widgets_values", [])):
                    graph[node_id]["inputs"][input_def["name"]] = node["widgets_values"][idx]

            for input_def in node.get("inputs", []):
                link_id = input_def.get("link")
                if link_id:
                    link = links.get(link_id)
                    if link:
                        src_node_id = str(link[1])
                        src_slot = link[2]
                        graph[node_id]["inputs"][input_def["name"]] = [src_node_id, src_slot]

        return graph
