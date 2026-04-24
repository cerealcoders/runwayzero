from runwayzero_agent import config


def test_config_reads_profiles_from_env(monkeypatch):
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_INSTANCE_ID", "i-test123")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_HOST", "10.0.0.1:8080")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_ROLE_NAME", "test-role")
    monkeypatch.setenv("RUNWAYZERO_APP_MODULE_DIR", "/tmp/app-dir")
    monkeypatch.setenv("CODECOMMIT_AWS_PROFILE", "my-codecommit-profile")
    monkeypatch.setenv("SSM_AWS_PROFILE", "my-ssm-profile")
    monkeypatch.setenv("DEMO_APP_REPO", "my-repo")
    monkeypatch.setenv("DEMO_APP_BRANCH", "my-branch")
    monkeypatch.setenv("DEMO_APP_REQUIREMENTS_PATH", "path/to/requirements.txt")
    cfg = config.load()
    assert cfg.codecommit_profile == "my-codecommit-profile"
    assert cfg.target_account_profile == "my-ssm-profile"
    assert cfg.demo_app_repo == "my-repo"
    assert cfg.demo_app_branch == "my-branch"
    assert cfg.requirements_path == "path/to/requirements.txt"
    assert cfg.target_instance_id == "i-test123"
    assert cfg.target_host == "10.0.0.1:8080"
    assert cfg.target_role_name == "test-role"
    assert cfg.app_module_dir == "/tmp/app-dir"
    assert cfg.fix_branch_name == "runwayzero/cve-2026-33626"


def test_config_profile_defaults_to_default(monkeypatch):
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_INSTANCE_ID", "i-test123")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_HOST", "10.0.0.1:8080")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_ROLE_NAME", "test-role")
    monkeypatch.setenv("RUNWAYZERO_APP_MODULE_DIR", "/tmp/app-dir")
    monkeypatch.delenv("CODECOMMIT_AWS_PROFILE", raising=False)
    monkeypatch.delenv("SSM_AWS_PROFILE", raising=False)
    cfg = config.load()
    assert cfg.codecommit_profile == "default"
    assert cfg.target_account_profile == "default"


def test_config_raises_when_target_instance_missing(monkeypatch):
    monkeypatch.delenv("RUNWAYZERO_TEST_EC2_INSTANCE_ID", raising=False)
    import pytest
    with pytest.raises(RuntimeError, match="RUNWAYZERO_TEST_EC2_INSTANCE_ID"):
        config.load()


def test_config_raises_when_role_name_missing(monkeypatch):
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_INSTANCE_ID", "i-test123")
    monkeypatch.setenv("RUNWAYZERO_TEST_EC2_HOST", "10.0.0.1:8080")
    monkeypatch.delenv("RUNWAYZERO_TEST_EC2_ROLE_NAME", raising=False)
    import pytest
    with pytest.raises(RuntimeError, match="RUNWAYZERO_TEST_EC2_ROLE_NAME"):
        config.load()
