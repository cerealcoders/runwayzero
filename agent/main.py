"""RunwayZero Agent entry point — CLI and Lambda handler."""

import argparse
import json
import sys


def cli():
    """CLI entry point: python -m agent.main CVE-2026-33626"""
    parser = argparse.ArgumentParser(description="RunwayZero Vulnerability Impact Agent")
    parser.add_argument("cve_id", help="CVE identifier to investigate (e.g. CVE-2026-33626)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = parser.parse_args()

    print(f"[RunwayZero] Investigating {args.cve_id}...")
    # TODO: Initialise Claude Agent SDK client with MCP server
    # TODO: Run agent loop


def lambda_handler(event, context):
    """AWS Lambda entry point for production deployment."""
    cve_id = event.get("cve_id") or event.get("detail", {}).get("cve_id")
    trigger = event.get("trigger", "manual")

    if not cve_id:
        return {"statusCode": 400, "body": json.dumps({"error": "cve_id required"})}

    print(f"[RunwayZero] Lambda triggered ({trigger}): {cve_id}")
    # TODO: Run agent loop
    return {"statusCode": 200, "body": json.dumps({"cve_id": cve_id, "status": "completed"})}


if __name__ == "__main__":
    cli()
