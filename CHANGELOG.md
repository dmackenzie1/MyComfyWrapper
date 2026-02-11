# Changelog

## Unreleased
- Refactored into application-oriented layout with explicit classes:
  - `PipelineApp`
  - `ImageDescriber`
  - `PromptService`
  - `ComfyApiClient`
- Added optional Ollama vision description mode with fallback to basic description.
- Added two-pass prompt generation:
  - pass 1 from image description
  - pass 2 for LoRA trigger-word + action-hint refinement
- Added `ACTION_HINT`, `ENABLE_VISION`, and `OLLAMA_VISION_MODEL` configuration support.
- Updated docs to reflect the new architecture and usage.
