#!/usr/bin/env bash
# pre-demo-check.sh — Verify all demo prerequisites before going on stage.
set -euo pipefail

EC2_ENDPOINT="${1:?Usage: pre-demo-check.sh <test-ec2-endpoint>}"
PROFILE_SSM="sia-nonprod-auto2"
PROFILE_CC="saml"
REGION="ap-southeast-1"

echo "=== Checking AWS profiles ==="
echo -n "SSM profile: "
aws sts get-caller-identity --profile "$PROFILE_SSM" --region "$REGION" --query "Arn" --output text
echo -n "CodeCommit profile: "
aws sts get-caller-identity --profile "$PROFILE_CC" --region "$REGION" --query "Arn" --output text

echo "=== Checking network reachability ==="
echo -n "Health check: "
curl -sf "$EC2_ENDPOINT/healthz" && echo " OK" || echo " FAILED"

echo "=== Checking API keys ==="
[ -n "${ANTHROPIC_API_KEY:-}" ] && echo "ANTHROPIC_API_KEY: set" || echo "ANTHROPIC_API_KEY: MISSING"
[ -n "${GENSPARK_API_KEY:-}" ] && echo "GENSPARK_API_KEY: set" || echo "GENSPARK_API_KEY: MISSING"

echo "=== Checking cached Genspark response ==="
[ -f cache/genspark_cve-2026-33626.json ] && echo "Cache: found" || echo "Cache: MISSING"

echo "=== Pre-demo check complete ==="
