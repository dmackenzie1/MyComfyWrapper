from __future__ import annotations

import argparse

from .application.pipeline import PipelineApp
from .config import build_config


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="my-comfy-wrapper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_flags(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--input-dir")
        subparser.add_argument("--workflow-template")
        subparser.add_argument("--lora-csv")
        subparser.add_argument("--output-dir")
        subparser.add_argument("--variants", type=int)
        subparser.add_argument("--seed", type=int)
        subparser.add_argument("--seed-strategy", choices=["random", "fixed", "increment"], default=None)
        subparser.add_argument("--comfy-base-url")
        subparser.add_argument("--ollama-base-url")
        subparser.add_argument("--ollama-model")
        subparser.add_argument("--ollama-vision-model")
        subparser.add_argument("--enable-vision", action="store_true")
        subparser.add_argument("--action-hint")
        subparser.add_argument("--concurrency", type=int)
        subparser.add_argument("--resume", action="store_true")
        subparser.add_argument("--workflow-node-overrides")

    run_parser = subparsers.add_parser("run", help="Run batch pipeline")
    add_common_flags(run_parser)
    run_parser.add_argument("--dry-run", action="store_true")

    inspect_parser = subparsers.add_parser("inspect-workflow", help="Inspect patch targets from workflow template")
    add_common_flags(inspect_parser)
    inspect_parser.add_argument("--dry-run", action="store_true")

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    config = build_config(args)

    for path_attr in ("workflow_template", "lora_csv"):
        path = getattr(config, path_attr)
        if not path.exists():
            raise FileNotFoundError(f"Required path not found: {path}")

    app = PipelineApp(config)
    if args.command == "inspect-workflow":
        for line in app.inspect_workflow():
            print(line)
        return

    app.run()


if __name__ == "__main__":
    main()
