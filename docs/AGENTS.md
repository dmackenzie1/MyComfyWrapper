# Agent Instructions for My Comfy Wrapper

## Working principles
- Always read existing repo files before changing assumptions.
- Keep changes small and coherent; avoid sweeping refactors in one step.
- Keep code junior-friendly: small classes, explicit names, minimal magic.
- Prefer stdlib where possible; if adding deps, justify them in docs.
- Ensure docs reflect reality; if not implemented, put it in `docs/TODO.md`.
- Add or update tests when touching workflow patching or CSV parsing.
- Never commit secrets; `.env` is gitignored and `.env.example` uses placeholders only.
- When modifying workflow patching, update `inspect-workflow` expectations and architecture docs.

## Local run (Windows + uv)
1. `uv sync`
2. `copy .env.example .env`
3. Edit `.env`
4. `uv run my-comfy-wrapper inspect-workflow --workflow-template wrappers/20260211-wan2-template.json`
5. `uv run my-comfy-wrapper run --input-dir inputs --workflow-template wrappers/20260211-wan2-template.json --lora-csv loras.csv --dry-run`

## Debug checklist
- **Comfy unreachable**: verify `COMFY_BASE_URL` and Comfy API availability.
- **Ollama unreachable**: verify `OLLAMA_BASE_URL`; first and second prompt passes should fall back.
- **Vision description not used**: verify `ENABLE_VISION=true` and `OLLAMA_VISION_MODEL`.
- **Workflow patch target not found**: run `inspect-workflow`, then use `WORKFLOW_NODE_OVERRIDES`.
- **Outputs missing**: inspect `submission_response.json`, `history_response.json`, and `manifest.json`.
