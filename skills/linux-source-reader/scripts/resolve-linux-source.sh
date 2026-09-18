#!/usr/bin/env bash
set -euo pipefail

target="${LINUX_SOURCE_DIR:-/opt/linux}"
ref="${LINUX_SOURCE_REF:-v7.1}"
repo="${LINUX_SOURCE_REPO:-https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git}"
allow_clone=1

usage() {
    cat <<'EOF'
Usage: resolve-linux-source.sh [OPTIONS]

Locate a Linux kernel source tree and print its absolute root path.

Resolution order:
  1. The current directory, or its enclosing Git worktree root
  2. /opt/linux (or the configured target)
  3. A fresh clone at the configured target

Options:
  --target DIR   Fallback checkout directory (default: /opt/linux)
  --ref REF      Git ref to clone (default: v7.1)
  --repo URL     Git repository to clone
  --no-clone     Only inspect existing trees; do not clone
  -h, --help     Show this help

Environment equivalents:
  LINUX_SOURCE_DIR, LINUX_SOURCE_REF, LINUX_SOURCE_REPO
EOF
}

die() {
    printf 'resolve-linux-source: %s\n' "$*" >&2
    exit 1
}

is_linux_tree() {
    local candidate="$1"

    [[ -d "$candidate" ]] || return 1
    [[ -f "$candidate/Makefile" ]] || return 1
    [[ -d "$candidate/arch" ]] || return 1
    [[ -d "$candidate/include/linux" ]] || return 1
    [[ -d "$candidate/init" ]] || return 1
    [[ -d "$candidate/kernel" ]] || return 1
    grep -Eq '^VERSION[[:space:]]*=[[:space:]]*[0-9]+' "$candidate/Makefile" || return 1
    grep -Eq '^PATCHLEVEL[[:space:]]*=[[:space:]]*[0-9]+' "$candidate/Makefile"
}

absolute_path() {
    local candidate="$1"
    (cd "$candidate" && pwd -P)
}

while (($#)); do
    case "$1" in
        --target)
            (($# >= 2)) || die "--target requires a directory"
            target="$2"
            shift 2
            ;;
        --ref)
            (($# >= 2)) || die "--ref requires a Git ref"
            ref="$2"
            shift 2
            ;;
        --repo)
            (($# >= 2)) || die "--repo requires a repository URL"
            repo="$2"
            shift 2
            ;;
        --no-clone)
            allow_clone=0
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1"
            ;;
    esac
done

if is_linux_tree "$PWD"; then
    absolute_path "$PWD"
    exit 0
fi

if command -v git >/dev/null 2>&1; then
    worktree_root="$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)"
    if [[ -n "$worktree_root" ]] && is_linux_tree "$worktree_root"; then
        absolute_path "$worktree_root"
        exit 0
    fi
fi

if is_linux_tree "$target"; then
    absolute_path "$target"
    exit 0
fi

if [[ -e "$target" ]]; then
    die "target exists but is not a Linux source tree: $target"
fi

((allow_clone)) || die "no Linux source tree found (clone disabled)"
command -v git >/dev/null 2>&1 || die "git is required to clone Linux source"

target_parent="$(dirname "$target")"
mkdir -p "$target_parent"
target_parent="$(absolute_path "$target_parent")"
target="$target_parent/$(basename "$target")"
clone_workspace="$(mktemp -d "$target_parent/.linux-source-clone.XXXXXX")"

cleanup() {
    rm -rf -- "$clone_workspace"
}
trap cleanup EXIT

printf 'resolve-linux-source: cloning %s (%s) into %s\n' "$repo" "$ref" "$target" >&2
git clone --filter=blob:none --depth 1 --single-branch --branch "$ref" -- "$repo" "$clone_workspace/source"

is_linux_tree "$clone_workspace/source" || die "cloned repository is not a valid Linux source tree"

if [[ -e "$target" ]]; then
    if is_linux_tree "$target"; then
        absolute_path "$target"
        exit 0
    fi
    die "target appeared during clone and is not a Linux source tree: $target"
fi

mv -- "$clone_workspace/source" "$target"
absolute_path "$target"
