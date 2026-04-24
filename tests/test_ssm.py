import json
from unittest.mock import MagicMock, patch

import pytest

from runwayzero_agent.tools.ssm import ssm_inventory_scan, ssm_run_command


@pytest.mark.asyncio
async def test_ssm_inventory_scan_returns_matching_instances():
    fake_session = MagicMock()
    fake_ssm = MagicMock()
    fake_session.client.return_value = fake_ssm
    fake_ssm.describe_instance_information.return_value = {
        "InstanceInformationList": [{"InstanceId": "i-test1234567890abc"}],
    }
    fake_ssm.list_inventory_entries.return_value = {
        "InstanceId": "i-test1234567890abc",
        "Entries": [
            {"Name": "lmdeploy", "Version": "0.12.2",
             "PackageId": "lmdeploy-0.12.2", "InstalledTime": "2026-04-22T00:00:00Z"},
        ],
    }
    with patch("runwayzero_agent.tools.ssm.boto3.Session", return_value=fake_session):
        result = await ssm_inventory_scan({"package": "lmdeploy"})
    payload = json.loads(result["content"][0]["text"])
    assert payload["matches"][0]["instance_id"] == "i-test1234567890abc"
    assert payload["matches"][0]["package"] == "lmdeploy"
    assert payload["matches"][0]["version"] == "0.12.2"
    assert "freshness_ts" in payload["matches"][0]


@pytest.mark.asyncio
async def test_ssm_run_command_succeeds_on_clean_exit():
    fake_session = MagicMock()
    fake_ssm = MagicMock()
    fake_session.client.return_value = fake_ssm
    fake_ssm.send_command.return_value = {"Command": {"CommandId": "cmd-123"}}
    fake_ssm.get_command_invocation.return_value = {
        "Status": "Success",
        "ResponseCode": 0,
        "StandardOutputContent": "patched\n",
        "StandardErrorContent": "",
    }
    with patch("runwayzero_agent.tools.ssm.boto3.Session", return_value=fake_session), \
         patch("runwayzero_agent.tools.ssm.time.sleep"):
        result = await ssm_run_command({
            "instance_id": "i-test1234567890abc",
            "commands": ["echo patched"],
            "timeout_s": 30,
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["status"] == "Success"
    assert payload["exit_code"] == 0
    assert "patched" in payload["stdout_tail"]
