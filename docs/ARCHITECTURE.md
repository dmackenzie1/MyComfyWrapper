# Architecture

## Application layout

- **PipelineApp** (`application/pipeline.py`): top-level batch orchestration.
- **ImageDescriber** (`services/image_describer.py`): description generation from image.
- **PromptService** (`services/prompt_service.py`): two-pass prompt generation/refinement.
- **ComfyApiClient** (`services/comfy_api.py`): ComfyUI HTTP integration.
- **WorkflowTemplate** (`workflow.py`): workflow target inspection + patching.
- **LoraCatalog** (`domain/lora.py`): LoRA CSV parsing and enabled selection.

## Pipeline steps

1. Load config (`CLI > env/.env > defaults`).
2. Load workflow template and inspect candidate patch targets.
3. Load LoRA CSV and keep enabled rows.
4. For each image + variant:
   - Build description with `ImageDescriber`.
     - Optional vision mode: sends the image to Ollama (`images` payload).
     - Fallback to basic mode (filename + sidecar) if vision is disabled or unavailable.
   - Prompt generation pass 1: build positive/negative from description.
   - Prompt generation pass 2: refine prompts with LoRA trigger words + action hint.
   - Patch workflow with prompts, seeds, LoRA settings, image path (best-effort), output prefix.
   - Dry-run: write artifacts and stop.
   - Real run: submit to Comfy, poll history, download outputs, write manifest.

## Workflow patching strategy

Targets are discovered by node metadata, not fixed IDs:
- `positive_prompt`: `CLIPTextEncode` title includes `positive`
- `negative_prompt`: `CLIPTextEncode` title includes `negative`
- `image_input`: image-like node types with widget inputs
- `save_prefix`: `SaveVideo` or `SaveImage`
- `sampler`: node type containing `Sampler`
- `lora`: `LoraLoader`

`inspect-workflow` prints candidates, selected node, and warnings for singleton ambiguity. `WORKFLOW_NODE_OVERRIDES` can force IDs.

## Resume and artifacts

- `--resume`: skips variant when `manifest.json` status is `completed`.
- Dry-run writes prompt/patch artifacts and a dry-run manifest only.
- Real run writes payload/response/history/manifest and downloaded files.
