#!/usr/bin/env bash
# Package a git repo into a zip + file tree for external model review.
# Usage: package-repo.sh [output_dir] [--scope path/to/dir]
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${1:-$HOME/Downloads/gpt-pro-bridge}"
SCOPE=""

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope) SCOPE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

ZIP_PATH="$OUTPUT_DIR/${REPO_NAME}-${TIMESTAMP}.zip"
TREE_PATH="$OUTPUT_DIR/file-tree.txt"

# Create zip via git archive — includes everything tracked in git, except dotfiles/dotdirs
# (e.g. .github, .vscode, .env*, .gitignore) and build artifacts (dist, build, coverage, out,
# Prisma generated client). Untracked files (node_modules, .next, etc.) are excluded by git.
PATHSPEC_FILE=$(mktemp)
trap 'rm -f "$PATHSPEC_FILE"' EXIT

if [[ -n "$SCOPE" ]]; then
  git -C "$REPO_ROOT" ls-files -- "$SCOPE" > "$PATHSPEC_FILE"
else
  git -C "$REPO_ROOT" ls-files \
    | grep -v -E '(^|/)\.[^/]' \
    | grep -v -E '(^|/)(dist|build|coverage|out)/' \
    | grep -v -E '(^|/)generated/' \
    > "$PATHSPEC_FILE"
fi

# git archive doesn't support --pathspec-from-file; xargs handles the file list
xargs git -C "$REPO_ROOT" archive --format=zip --prefix="${REPO_NAME}/" HEAD -- < "$PATHSPEC_FILE" > "$ZIP_PATH"

ZIP_SIZE=$(du -h "$ZIP_PATH" | cut -f1 | xargs)

# Generate compact first-level tree (excludes noise like migrations, lock files, test fixtures)
COMPACT_TREE_PATH="$OUTPUT_DIR/tree-compact.txt"

if [[ -n "$SCOPE" ]]; then
  # Scoped: show first two levels within the scope
  git -C "$REPO_ROOT" ls-files -- "$SCOPE" \
    | sed "s|^${SCOPE}/||" \
    | cut -d/ -f1-2 \
    | sort -u > "$COMPACT_TREE_PATH"
else
  # Full repo: top-level files + first level of each directory
  # Exclude: lock files, migration SQL, test fixtures, config noise
  git -C "$REPO_ROOT" ls-files \
    | grep -v -E '(pnpm-lock\.yaml|migrations/.*/migration\.sql|\.gitkeep)' \
    | awk -F/ '{
        if (NF == 1) print $0           # top-level files
        else if (NF == 2) print $1 "/" $2  # first-level entries
        else print $1 "/" $2 "/"          # directories shown as dir/subdir/
      }' \
    | sort -u > "$COMPACT_TREE_PATH"
fi

COMPACT_COUNT=$(wc -l < "$COMPACT_TREE_PATH" | xargs)

# Summary
cat <<EOF
=== GPT Pro Bridge Package ===
Zip:    $ZIP_PATH ($ZIP_SIZE)
Tree:   $COMPACT_TREE_PATH ($COMPACT_COUNT entries)
Scope:  ${SCOPE:-entire repo}
EOF
