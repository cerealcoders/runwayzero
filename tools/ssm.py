"""AWS Systems Manager tools — inventory scan and run command."""

import boto3

from agent.config import AWS_PROFILE_SSM, AWS_REGION


def _ssm_client():
    session = boto3.Session(profile_name=AWS_PROFILE_SSM, region_name=AWS_REGION)
    return session.client("ssm")


def ssm_inventory_scan(package: str) -> dict:
    """Scan SSM Inventory for instances running the given package.

    Returns:
        {matches: [{instance_id, package, version, app_tag, environment, freshness_ts}],
         inventory_age_seconds: int}
    """
    # TODO: Implement SSM Inventory query
    return {"error": "Not implemented", "retryable": False, "details": {}}


def ssm_run_command(instance_id: str, commands: list[str], timeout_s: int = 120) -> dict:
    """Execute commands on an EC2 instance via SSM Run Command.

    Returns:
        {status, command_id, exit_code, stdout_tail, stderr_tail, duration_s}
    """
    # TODO: Implement SSM SendCommand + poll for result
    return {"error": "Not implemented", "retryable": False, "details": {}}
