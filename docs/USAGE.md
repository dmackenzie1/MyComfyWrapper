# Usage

## Inspect workflow patch targets

```bash
uv run my-comfy-wrapper inspect-workflow \
  --workflow-template wrappers/20260211-wan2-template.json
```

## Dry run

```bash
uv run my-comfy-wrapper run \
  --input-dir inputs \
  --workflow-template wrappers/20260211-wan2-template.json \
  --lora-csv loras.csv \
  --output-dir outputs \
  --variants 2 \
  --dry-run
```

## Dry run with action + vision

```bash
uv run my-comfy-wrapper run \
  --input-dir inputs \
  --workflow-template wrappers/20260211-wan2-template.json \
  --lora-csv loras.csv \
  --action-hint "slow camera push with subtle character motion" \
  --enable-vision \
  --ollama-vision-model llava:7b \
  --dry-run
```

## Real run + resume

```bash
uv run my-comfy-wrapper run \
  --input-dir inputs \
  --workflow-template wrappers/20260211-wan2-template.json \
  --lora-csv loras.csv \
  --output-dir outputs \
  --resume
```
