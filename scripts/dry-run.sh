#!/usr/bin/env bash
# Run the agent end-to-end against the live test-ec2 and capture the log.
# Usage: scripts/dry-run.sh [CVE-ID]
set -euo pipefail

CVE_ID="${1:-CVE-2026-33626}"
TS=$(date +%Y%m%d-%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${PROJECT_DIR}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/dry-run-${TS}.log"

echo "[dry-run] CVE=$CVE_ID"
echo "[dry-run] log file: $LOG_FILE"
cd "$PROJECT_DIR"

# shellcheck disable=SC1091
[ -f .env ] && source .env

.venv/bin/python -m runwayzero_agent.agent "$CVE_ID" 2>&1 | tee "$LOG_FILE"

echo "[dry-run] DONE — log saved to $LOG_FILE"
