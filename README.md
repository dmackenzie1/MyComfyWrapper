# My Comfy Wrapper

CLI-first Python application to batch patch and run a ComfyUI workflow template from local images.

## What was originally in this repository

Before bootstrap, the repo contained:
- `README.md` with only the project title.
- `wrappers/20260211-wan2-template.json`, with positive/negative `CLIPTextEncode`, `LoraLoader`, `KSamplerAdvanced`, and `SaveVideo` nodes.

## Phase 1 (implemented now)

- Batch image processing (`run` command).
- Workflow patch inspection (`inspect-workflow` command).
- Image description flow:
  - basic mode (filename + sidecar metadata)
  - optional vision mode via Ollama image input with fallback to basic mode
- Two-pass prompt generation via Ollama:
  1) base positive/negative prompts from image description
  2) refinement pass that injects LoRA trigger words and action hint
- LoRA CSV parsing and enabled-row selection.
- Workflow patching without hardcoded IDs (class/type/title discovery + optional overrides).
- ComfyUI submit/wait/download integration.
- Dry-run and resume support.

## Project structure (application style)

- `src/my_comfy_wrapper/application/pipeline.py` – top-level orchestration (`PipelineApp`)
- `src/my_comfy_wrapper/services/image_describer.py` – image description class
- `src/my_comfy_wrapper/services/prompt_service.py` – two-pass prompt generation class
- `src/my_comfy_wrapper/services/comfy_api.py` – Comfy API class
- `src/my_comfy_wrapper/workflow.py` – workflow inspect/patch logic
- `src/my_comfy_wrapper/domain/lora.py` – LoRA domain model/catalog

## Quickstart (Windows + uv)

```bash
uv sync
copy .env.example .env
```

Edit `.env`, then:

```bash
uv run my-comfy-wrapper inspect-workflow --workflow-template wrappers/20260211-wan2-template.json
uv run my-comfy-wrapper run --input-dir inputs --workflow-template wrappers/20260211-wan2-template.json --lora-csv loras.csv --output-dir outputs --dry-run
uv run my-comfy-wrapper run --input-dir inputs --workflow-template wrappers/20260211-wan2-template.json --lora-csv loras.csv --output-dir outputs --resume
```

## Example with LoRA/action-aware refinement

```bash
uv run my-comfy-wrapper run \
  --input-dir inputs \
  --workflow-template wrappers/20260211-wan2-template.json \
  --lora-csv loras.csv \
  --action-hint "slow camera push-in with subtle hair and cloth motion" \
  --dry-run
```

## Output layout

`outputs/<image_id>/variant_<n>/` includes patched workflow, prompts, selected LoRAs, submission/history metadata, and downloaded files.
