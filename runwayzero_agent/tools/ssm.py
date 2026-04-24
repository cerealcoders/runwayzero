import time
from typing import Any

import boto3

from runwayzero_agent import config
from runwayzero_agent.errors import error_response, success_response
from runwayzero_agent.tool_registry import register_tool


def _ssm_client():
    cfg = config.load()
    return boto3.Session(profile_name=cfg.target_account_profile).client(
        "ssm", region_name=cfg.region
    )


async def ssm_inventory_scan(args: dict[str, Any]) -> dict[str, Any]:
    package = args["package"]
    try:
        ssm = _ssm_client()
        instances = ssm.describe_instance_information()["InstanceInformationList"]
        matches: list[dict[str, Any]] = []
        for inst in instances:
            entries = ssm.list_inventory_entries(
                InstanceId=inst["InstanceId"],
                TypeName="AWS:Application",
            )
            for e in entries.get("Entries", []):
                if e.get("Name") == package:
                    matches.append({
                        "instance_id": inst["InstanceId"],
                        "package": e["Name"],
                        "version": e.get("Version", "unknown"),
                        "freshness_ts": e.get("InstalledTime", "unknown"),
                    })
        return success_response({
            "matches": matches,
            "inventory_note": "EC2 tag enrichment intentionally omitted — describe_instance_information does not return tags. Owner resolution happens via the hardcoded demo team mapping in the agent's system prompt.",
        })
    except Exception as exc:
        return error_response(f"SSM inventory scan failed: {exc}", retryable=True)


async def ssm_run_command(args: dict[str, Any]) -> dict[str, Any]:
    instance_id = args["instance_id"]
    commands = args["commands"]
    timeout_s = int(args.get("timeout_s", 120))
    try:
        ssm = _ssm_client()
        cmd = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": commands},
        )["Command"]["CommandId"]
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            inv = ssm.get_command_invocation(CommandId=cmd, InstanceId=instance_id)
            status = inv["Status"]
            if status in {"Success", "Failed", "Cancelled", "TimedOut"}:
                return success_response({
                    "status": status,
                    "command_id": cmd,
                    "exit_code": inv.get("ResponseCode", -1),
                    "stdout_tail": inv.get("StandardOutputContent", "")[-2000:],
                    "stderr_tail": inv.get("StandardErrorContent", "")[-2000:],
                    "duration_s": int(timeout_s - (deadline - time.time())),
                })
            time.sleep(2)
        return error_response(
            f"SSM command timed out after {timeout_s}s",
            retryable=True,
            details={"command_id": cmd},
        )
    except Exception as exc:
        return error_response(f"SSM run_command failed: {exc}", retryable=True)


register_tool(
    name="ssm_inventory_scan",
    description="Find managed EC2 instances reporting a given pip-installed package. Returns instance id, package version, and freshness only — owner resolution is hardcoded in this demo.",
    input_schema={
        "type": "object",
        "properties": {
            "package": {"type": "string", "description": "pip package name to look up in SSM inventory"},
        },
        "required": ["package"],
    },
    fn=ssm_inventory_scan,
)

register_tool(
    name="ssm_run_command",
    description="Run a shell command on a managed EC2 instance and poll until completion",
    input_schema={
        "type": "object",
        "properties": {
            "instance_id": {"type": "string"},
            "commands": {"type": "array", "items": {"type": "string"}},
            "timeout_s": {"type": "integer", "default": 120},
        },
        "required": ["instance_id", "commands"],
    },
    fn=ssm_run_command,
)
