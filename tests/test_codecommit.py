import json
from unittest.mock import MagicMock, patch

import pytest

from runwayzero_agent.tools.codecommit import (
    codecommit_get_file,
    codecommit_put_file,
    codecommit_create_pull_request,
    codecommit_post_pr_comment,
    codecommit_merge_pull_request,
)


@pytest.mark.asyncio
async def test_codecommit_get_file_returns_content_and_commit():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    fake_cc.get_file.return_value = {
        "fileContent": b"lmdeploy==0.12.2\n",
        "blobId": "blob123",
        "commitId": "commit456",
    }
    fake_cc.get_branch.return_value = {"branch": {"commitId": "commit456"}}
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_get_file({
            "repo": "demo-app", "branch": "main",
            "path": "platform/files/runwayzero/requirements.txt",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["content"] == "lmdeploy==0.12.2\n"
    assert payload["blob_id"] == "blob123"
    assert payload["parent_commit_id"] == "commit456"
    assert payload["branch_head_commit_id"] == "commit456"


@pytest.mark.asyncio
async def test_codecommit_put_file_creates_branch_when_absent():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    from botocore.exceptions import ClientError
    fake_cc.get_branch.side_effect = [
        ClientError({"Error": {"Code": "BranchDoesNotExistException"}}, "GetBranch"),
    ]
    fake_cc.create_branch.return_value = {}
    fake_cc.put_file.return_value = {"commitId": "newcommit"}
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_put_file({
            "repo": "demo-app",
            "branch": "runwayzero/cve-2026-33626",
            "path": "platform/files/runwayzero/requirements.txt",
            "content": "lmdeploy==0.12.3\n",
            "parent_commit_id": "commit456",
            "source_branch": "main",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["commit_id"] == "newcommit"
    assert payload["branch"] == "runwayzero/cve-2026-33626"
    assert payload["branch_existed_before"] is False
    fake_cc.create_branch.assert_called_once_with(
        repositoryName="demo-app",
        branchName="runwayzero/cve-2026-33626",
        commitId="commit456",
    )


@pytest.mark.asyncio
async def test_codecommit_put_file_skips_create_branch_when_present():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    fake_cc.get_branch.return_value = {"branch": {"commitId": "existing-head"}}
    fake_cc.put_file.return_value = {"commitId": "newcommit"}
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_put_file({
            "repo": "demo-app",
            "branch": "runwayzero/cve-2026-33626",
            "path": "platform/files/runwayzero/requirements.txt",
            "content": "lmdeploy==0.12.3\n",
            "parent_commit_id": "commit456",
            "source_branch": "main",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["branch_existed_before"] is True
    fake_cc.create_branch.assert_not_called()
    put_call = fake_cc.put_file.call_args.kwargs
    assert put_call["parentCommitId"] == "existing-head"


@pytest.mark.asyncio
async def test_codecommit_create_pr_returns_id_and_url():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    fake_cc.create_pull_request.return_value = {
        "pullRequest": {"pullRequestId": "42", "pullRequestStatus": "OPEN"},
    }
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_create_pull_request({
            "repo": "demo-app",
            "title": "[RunwayZero] CVE-2026-33626",
            "source_branch": "runwayzero/cve-2026-33626",
            "dest_branch": "main",
            "description": "auto-fix",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["pr_id"] == "42"
    assert payload["status"] == "OPEN"
    assert "console.aws.amazon.com" in payload["web_url"]


@pytest.mark.asyncio
async def test_codecommit_post_pr_comment_returns_comment_id():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    fake_cc.post_comment_for_pull_request.return_value = {"comment": {"commentId": "c1"}}
    fake_cc.get_pull_request.return_value = {
        "pullRequest": {
            "pullRequestTargets": [{
                "repositoryName": "demo-app",
                "sourceCommit": "src", "destinationCommit": "dst",
            }],
        },
    }
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_post_pr_comment({
            "repo": "demo-app", "pr_id": "42", "body": "tests: 1 passed in 0.5s",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["comment_id"] == "c1"


@pytest.mark.asyncio
async def test_codecommit_merge_returns_post_merge_head():
    fake_session = MagicMock()
    fake_cc = MagicMock()
    fake_session.client.return_value = fake_cc
    fake_cc.merge_pull_request_by_fast_forward.return_value = {
        "pullRequest": {
            "pullRequestId": "42",
            "pullRequestStatus": "CLOSED",
            "pullRequestTargets": [{"destinationReference": "refs/heads/main"}],
        },
    }
    fake_cc.get_branch.return_value = {"branch": {"commitId": "merged-head"}}
    with patch("runwayzero_agent.tools.codecommit.boto3.Session", return_value=fake_session):
        result = await codecommit_merge_pull_request({
            "repo": "demo-app", "pr_id": "42", "strategy": "FAST_FORWARD",
        })
    payload = json.loads(result["content"][0]["text"])
    assert payload["merged"] is True
    assert payload["post_merge_branch_head"] == "merged-head"
