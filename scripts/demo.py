#!/usr/bin/env python3
import argparse
import json
import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
    tools = [t.get("name") for t in cfg.get("tools", [])]
    payload = {
        "tools": tools,
        "status": "demo",
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
