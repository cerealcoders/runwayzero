from typing import Any

import boto3
from botocore.exceptions import ClientError

from runwayzero_agent import config
from runwayzero_agent.errors import error_response, success_response
from runwayzero_agent.tool_registry import register_tool


def _cc_client():
    cfg = config.load()
    return boto3.Session(profile_name=cfg.codecommit_profile).client(
        "codecommit", region_name=cfg.region
    )


async def codecommit_get_file(args: dict[str, Any]) -> dict[str, Any]:
    try:
        cc = _cc_client()
        f = cc.get_file(
            repositoryName=args["repo"],
            commitSpecifier=args["branch"],
            filePath=args["path"],
        )
        head = cc.get_branch(repositoryName=args["repo"], branchName=args["branch"])
        return success_response({
            "content": f["fileContent"].decode("utf-8"),
            "blob_id": f["blobId"],
            "parent_commit_id": f["commitId"],
            "branch_head_commit_id": head["branch"]["commitId"],
        })
    except Exception as exc:
        return error_response(f"CodeCommit get_file failed: {exc}", retryable=False)


async def codecommit_put_file(args: dict[str, Any]) -> dict[str, Any]:
    try:
        cc = _cc_client()
        repo = args["repo"]
        branch = args["branch"]
        existed_before = True
        parent_commit_id = args["parent_commit_id"]
        try:
            existing = cc.get_branch(repositoryName=repo, branchName=branch)
            parent_commit_id = existing["branch"]["commitId"]
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "BranchDoesNotExistException":
                existed_before = False
                cc.create_branch(
                    repositoryName=repo,
                    branchName=branch,
                    commitId=parent_commit_id,
                )
            else:
                raise
        result = cc.put_file(
            repositoryName=repo,
            branchName=branch,
            fileContent=args["content"].encode("utf-8"),
            filePath=args["path"],
            parentCommitId=parent_commit_id,
            commitMessage="RunwayZero: bump lmdeploy to fixed version (CVE-2026-33626)",
            name="RunwayZero Agent",
            email="runwayzero-agent@example.com",
        )
        return success_response({
            "commit_id": result["commitId"],
            "branch": branch,
            "branch_existed_before": existed_before,
        })
    except Exception as exc:
        return error_response(f"CodeCommit put_file failed: {exc}", retryable=False)


async def codecommit_create_pull_request(args: dict[str, Any]) -> dict[str, Any]:
    try:
        cc = _cc_client()
        cfg = config.load()
        pr = cc.create_pull_request(
            title=args["title"],
            description=args.get("description", ""),
            targets=[{
                "repositoryName": args["repo"],
                "sourceReference": args["source_branch"],
                "destinationReference": args["dest_branch"],
            }],
        )["pullRequest"]
        web_url = (
            f"https://console.aws.amazon.com/codesuite/codecommit/repositories/"
            f"{args['repo']}/pull-requests/{pr['pullRequestId']}/details?region={cfg.region}"
        )
        return success_response({
            "pr_id": pr["pullRequestId"],
            "status": pr["pullRequestStatus"],
            "web_url": web_url,
        })
    except Exception as exc:
        return error_response(f"create_pull_request failed: {exc}", retryable=False)


async def codecommit_post_pr_comment(args: dict[str, Any]) -> dict[str, Any]:
    try:
        cc = _cc_client()
        pr = cc.get_pull_request(pullRequestId=args["pr_id"])["pullRequest"]
        target = pr["pullRequestTargets"][0]
        comment = cc.post_comment_for_pull_request(
            pullRequestId=args["pr_id"],
            repositoryName=args["repo"],
            beforeCommitId=target["destinationCommit"],
            afterCommitId=target["sourceCommit"],
            content=args["body"],
        )["comment"]
        return success_response({"comment_id": comment["commentId"]})
    except Exception as exc:
        return error_response(f"post_pr_comment failed: {exc}", retryable=False)


async def codecommit_merge_pull_request(args: dict[str, Any]) -> dict[str, Any]:
    try:
        cc = _cc_client()
        strategy = args.get("strategy", "FAST_FORWARD").upper()
        if strategy != "FAST_FORWARD":
            return error_response(
                f"Only FAST_FORWARD strategy is supported in this demo, got {strategy}",
                retryable=False,
            )
        merged = cc.merge_pull_request_by_fast_forward(
            pullRequestId=args["pr_id"],
            repositoryName=args["repo"],
        )["pullRequest"]
        dest_branch_name = merged.get("pullRequestTargets", [{}])[0].get(
            "destinationReference", "main"
        ).split("refs/heads/")[-1]
        head = cc.get_branch(
            repositoryName=args["repo"], branchName=dest_branch_name,
        )["branch"]["commitId"]
        return success_response({
            "merged": merged["pullRequestStatus"] == "CLOSED",
            "merge_commit_id": head,
            "post_merge_branch_head": head,
        })
    except Exception as exc:
        return error_response(f"merge_pull_request failed: {exc}", retryable=False)


_SCHEMA_REPO_BRANCH_PATH = {
    "type": "object",
    "properties": {
        "repo": {"type": "string"},
        "branch": {"type": "string"},
        "path": {"type": "string"},
    },
    "required": ["repo", "branch", "path"],
}

register_tool(
    name="codecommit_get_file",
    description="Read a file from a CodeCommit repo branch",
    input_schema=_SCHEMA_REPO_BRANCH_PATH,
    fn=codecommit_get_file,
)

register_tool(
    name="codecommit_put_file",
    description="Write a file to a CodeCommit branch (creating the branch off source_branch if absent) and return the commit id",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "branch": {"type": "string"},
            "path": {"type": "string"},
            "content": {"type": "string"},
            "parent_commit_id": {"type": "string"},
            "source_branch": {"type": "string"},
        },
        "required": ["repo", "branch", "path", "content", "parent_commit_id", "source_branch"],
    },
    fn=codecommit_put_file,
)

register_tool(
    name="codecommit_create_pull_request",
    description="Open a pull request from source_branch into dest_branch",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "title": {"type": "string"},
            "source_branch": {"type": "string"},
            "dest_branch": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["repo", "title", "source_branch", "dest_branch"],
    },
    fn=codecommit_create_pull_request,
)

register_tool(
    name="codecommit_post_pr_comment",
    description="Add a comment to a pull request (used to attach test results)",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "pr_id": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["repo", "pr_id", "body"],
    },
    fn=codecommit_post_pr_comment,
)

register_tool(
    name="codecommit_merge_pull_request",
    description="Merge a pull request and return the post-merge destination branch head commit",
    input_schema={
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "pr_id": {"type": "string"},
            "strategy": {"type": "string", "enum": ["FAST_FORWARD"]},
        },
        "required": ["repo", "pr_id", "strategy"],
    },
    fn=codecommit_merge_pull_request,
)
