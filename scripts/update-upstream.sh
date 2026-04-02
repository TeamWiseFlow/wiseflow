#!/bin/bash
# ⚠️  DEPRECATED — use scripts/upgrade.sh instead
#
# This script has been merged into upgrade.sh, which:
#   - Handles both OFB code and openclaw engine updates in one step
#   - Respects the openclaw.version pin (no more tracking main blindly)
#   - Calls apply-addons.sh (which already includes setup-crew.sh)
#
echo ""
echo "⚠️  update-upstream.sh is deprecated."
echo "   Please use:  ./scripts/upgrade.sh"
echo ""
exec "$(dirname "$0")/upgrade.sh" "$@"
