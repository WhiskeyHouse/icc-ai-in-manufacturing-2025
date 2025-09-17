# 🐛 Bug Fix: Unbound Variable Error

## Issue
The shell script `run-linting-demo.sh` was throwing an "unbound variable" error when run without the `--auto` flag due to the `set -euo pipefail` setting.

## Error Message
```bash
./run-linting-demo.sh: line 38: $1: unbound variable
```

## Root Cause
The script was checking `$1` directly without handling the case where no arguments were provided. With `set -u` (unbound variable checking), this caused the script to fail.

## Fix Applied
Changed the parameter expansion from:
```bash
if [[ "$1" == "--auto" ]]; then
```

To:
```bash
if [[ "${1:-}" == "--auto" ]]; then
```

## Explanation
- `${1:-}` uses parameter expansion with a default empty string
- If `$1` is unset or null, it returns an empty string instead of failing
- This allows the script to work both with and without arguments

## Testing
✅ **Without arguments**: `./run-linting-demo.sh` - Works correctly  
✅ **With auto flag**: `./run-linting-demo.sh --auto` - Works correctly  
✅ **Interactive mode**: All menu options work properly  

## Status
🎉 **FIXED** - Both interactive and auto modes now work correctly without any unbound variable errors.
