from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    region: str
    codecommit_profile: str
    target_account_profile: str
    demo_app_repo: str
    demo_app_branch: str
    requirements_path: str
    fix_branch_name: str
    fix_pr_title: str
    target_instance_id: str
    target_host: str
    target_role_name: str
    app_module_dir: str


def _required(name: str, hint: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"{name} must be set ({hint})")
    return val


def load() -> Config:
    return Config(
        region=os.environ.get("AWS_REGION", "ap-southeast-1"),
        codecommit_profile=os.environ.get("CODECOMMIT_AWS_PROFILE", "default"),
        target_account_profile=os.environ.get("SSM_AWS_PROFILE", "default"),
        demo_app_repo=os.environ.get("DEMO_APP_REPO", "demo-app"),
        demo_app_branch=os.environ.get("DEMO_APP_BRANCH", "main"),
        requirements_path=os.environ.get("DEMO_APP_REQUIREMENTS_PATH", "requirements.txt"),
        fix_branch_name="runwayzero/cve-2026-33626",
        fix_pr_title="[RunwayZero] CVE-2026-33626: bump lmdeploy 0.12.2 -> 0.12.3",
        target_instance_id=_required(
            "RUNWAYZERO_TEST_EC2_INSTANCE_ID",
            "run Phase A8 to discover it"
        ),
        target_host=_required(
            "RUNWAYZERO_TEST_EC2_HOST",
            "e.g. 10.0.0.1:8080"
        ),
        target_role_name=_required(
            "RUNWAYZERO_TEST_EC2_ROLE_NAME",
            "the role name IMDS returns; see Phase A8 step 4"
        ),
        app_module_dir=_required(
            "RUNWAYZERO_APP_MODULE_DIR",
            "absolute path to dir containing app.py for sandbox PYTHONPATH"
        ),
    )
