# Configuration

## Precedence

1. CLI flags
2. Environment variables (`.env` supported)
3. Built-in defaults

## Environment variables

- Paths: `INPUT_DIR`, `WORKFLOW_TEMPLATE`, `LORA_CSV`, `OUTPUT_DIR`
- Runtime: `VARIANTS`, `SEED`, `SEED_STRATEGY`, `CONCURRENCY`, `RESUME`, `ACTION_HINT`
- Services: `COMFY_BASE_URL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- Vision: `ENABLE_VISION`, `OLLAMA_VISION_MODEL`
- Workflow mapping override: `WORKFLOW_NODE_OVERRIDES` (JSON string)

## CLI overrides

Every env var has a matching CLI flag (for example `--action-hint`, `--enable-vision`, `--ollama-vision-model`).

## LoRA CSV schema

Required columns:
- `name_or_path`
- `weight` (float)
- `trigger_words`
- `enabled` (boolean-like: `true/false`, `1/0`, `yes/no`, `on/off`)

Validation:
- file must exist
- required header columns must exist
- each `weight` must parse as float

Example:

```csv
name_or_path,weight,trigger_words,enabled
high/wan2_high.safetensors,1.0,"cinematic detailed lighting",true
low/wan2_low.safetensors,0.8,"smooth motion",false
```
