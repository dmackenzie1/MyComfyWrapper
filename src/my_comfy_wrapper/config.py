from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    input_dir: Path
    workflow_template: Path
    lora_csv: Path
    output_dir: Path
    variants: int
    seed: int | None
    seed_strategy: str
    comfy_base_url: str
    ollama_base_url: str
    ollama_model: str
    ollama_vision_model: str | None
    enable_vision: bool
    action_hint: str
    concurrency: int
    resume: bool
    dry_run: bool
    workflow_node_overrides: dict[str, int]


def _load_dotenv_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def build_config(args) -> AppConfig:
    _load_dotenv_file()
    overrides_raw = args.workflow_node_overrides or os.getenv("WORKFLOW_NODE_OVERRIDES", "{}")
    try:
        workflow_node_overrides = json.loads(overrides_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("WORKFLOW_NODE_OVERRIDES must be valid JSON.") from exc

    return AppConfig(
        input_dir=Path(args.input_dir or os.getenv("INPUT_DIR", "inputs")),
        workflow_template=Path(args.workflow_template or os.getenv("WORKFLOW_TEMPLATE", "wrappers/20260211-wan2-template.json")),
        lora_csv=Path(args.lora_csv or os.getenv("LORA_CSV", "loras.csv")),
        output_dir=Path(args.output_dir or os.getenv("OUTPUT_DIR", "outputs")),
        variants=int(args.variants or os.getenv("VARIANTS", "1")),
        seed=args.seed if args.seed is not None else (int(os.getenv("SEED")) if os.getenv("SEED") else None),
        seed_strategy=args.seed_strategy or os.getenv("SEED_STRATEGY", "random"),
        comfy_base_url=(args.comfy_base_url or os.getenv("COMFY_BASE_URL", "http://127.0.0.1:8188")).rstrip("/"),
        ollama_base_url=(args.ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/"),
        ollama_model=args.ollama_model or os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        ollama_vision_model=args.ollama_vision_model or os.getenv("OLLAMA_VISION_MODEL") or None,
        enable_vision=args.enable_vision or _env_bool("ENABLE_VISION", False),
        action_hint=args.action_hint or os.getenv("ACTION_HINT", ""),
        concurrency=int(args.concurrency or os.getenv("CONCURRENCY", "1")),
        resume=args.resume or _env_bool("RESUME", False),
        dry_run=getattr(args, "dry_run", False),
        workflow_node_overrides={str(k): int(v) for k, v in workflow_node_overrides.items()},
    )
