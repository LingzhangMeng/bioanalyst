#!/usr/bin/env bash
# install.sh — install the `bioanalyst` skill into an AI agent's skill root.
#
# Usage:
#   ./install.sh                 # symlink into ~/.reasonix/skills/bioanalyst (default)
#   SKILLS_ROOT=/path ./install.sh   # or any agent skill root
#   ./install.sh --copy          # copy instead of symlink
#   ./install.sh --check         # verify the skill tree is complete and valid
#   ./install.sh --unlink        # remove the installed link/copy
#   ./install.sh --path          # print the [skills].paths snippet for reasonix config.toml
#
# Safe by design: refuses to overwrite a real directory; --unlink only removes a symlink
# or a directory it can identify as an installed copy.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$HERE/.." && pwd)"
NAME="$(basename "$SKILL_DIR")"
ROOT="${SKILLS_ROOT:-$HOME/.reasonix/skills}"
TARGET="$ROOT/$NAME"

c_ok()   { printf '\033[32m✅\033[0m %s\n' "$*"; }
c_warn() { printf '\033[33m⚠️ \033[0m %s\n' "$*"; }
c_err()  { printf '\033[31m❌\033[0m %s\n' "$*" >&2; }

check_tree() {
  local fail=0
  [ -f "$SKILL_DIR/SKILL.md" ] || { c_err "SKILL.md missing"; fail=1; }
  if [ -f "$SKILL_DIR/SKILL.md" ]; then
    head -5 "$SKILL_DIR/SKILL.md" | grep -q '^---$' || { c_err "SKILL.md has no YAML frontmatter"; fail=1; }
    grep -q '^name: *'"$NAME" "$SKILL_DIR/SKILL.md" \
      || { c_warn "frontmatter name does not match directory name ($NAME)"; }
    grep -q '^description:' "$SKILL_DIR/SKILL.md" || { c_err "frontmatter has no description"; fail=1; }
  fi
  local n_ref n_tpl
  n_ref=$(find "$SKILL_DIR/references" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
  n_tpl=$(find "$SKILL_DIR/templates" -type f 2>/dev/null | wc -l | tr -d ' ')
  [ "$n_ref" -ge 1 ] || { c_err "references/ is empty"; fail=1; }
  [ "$n_tpl" -ge 1 ] || { c_err "templates/ is empty"; fail=1; }
  python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$SKILL_DIR/scripts/bap.py" 2>/dev/null \
    || { c_err "scripts/bap.py does not parse"; fail=1; }
  bash -n "$SKILL_DIR/scripts/install.sh" 2>/dev/null || true
  if command -v Rscript >/dev/null 2>&1; then
    Rscript -e "invisible(parse('$SKILL_DIR/scripts/env_capture.R'))" 2>/dev/null \
      || { c_err "scripts/env_capture.R does not parse"; fail=1; }
  else
    c_warn "Rscript not found — skipped R syntax check"
  fi
  echo "   references: $n_ref .md   templates: $n_tpl files   scripts: $(find "$SKILL_DIR/scripts" -type f | wc -l | tr -d ' ')"
  return $fail
}

case "${1:-}" in
  --check)
    echo "Checking skill tree: $SKILL_DIR"
    if check_tree; then c_ok "skill tree valid"; else c_err "skill tree has problems"; exit 1; fi
    python3 "$SKILL_DIR/scripts/bap.py" --version
    exit 0
    ;;
  --path)
    cat <<EOF
# Add this to ~/.reasonix/config.toml under [skills], then restart the agent:
[skills]
paths = [ "$(dirname "$SKILL_DIR")" ]     # merge into the existing paths array
max_depth = 3

# The skill is then discovered as: $NAME
EOF
    exit 0
    ;;
  --unlink)
    if [ -L "$TARGET" ]; then rm "$TARGET"; c_ok "removed symlink $TARGET"
    elif [ -d "$TARGET" ] && [ -f "$TARGET/SKILL.md" ] && grep -q "name: *$NAME" "$TARGET/SKILL.md"; then
      rm -rf "$TARGET"; c_ok "removed installed copy $TARGET"
    elif [ -e "$TARGET" ]; then c_err "$TARGET exists and is not an installed $NAME skill — refusing"; exit 1
    else c_warn "nothing installed at $TARGET"; fi
    exit 0
    ;;
  --copy)
    [ -e "$TARGET" ] && { c_err "$TARGET already exists — run --unlink first"; exit 1; }
    mkdir -p "$ROOT"; cp -r "$SKILL_DIR" "$TARGET"; c_ok "copied to $TARGET"
    ;;
  "")
    check_tree || { c_err "refusing to install an incomplete skill"; exit 1; }
    mkdir -p "$ROOT"
    if [ -L "$TARGET" ]; then
      c_warn "already linked: $TARGET"; exit 0
    elif [ -e "$TARGET" ]; then
      c_err "$TARGET already exists (not a symlink) — run --unlink first, or use --path"; exit 1
    fi
    ln -s "$SKILL_DIR" "$TARGET"; c_ok "linked $TARGET -> $SKILL_DIR"
    ;;
  *)
    c_err "unknown option: $1"; sed -n '3,14p' "$0"; exit 2
    ;;
esac

cat <<EOF

Installed skill: $NAME
  Invoke (reasonix):        run_skill({ name: "$NAME" })   or   /$NAME
  Skill file:               $TARGET/SKILL.md
  Utility CLI:              python3 $TARGET/scripts/bap.py --help
  Smoke test:               $TARGET/scripts/install.sh --check
  Remove:                   $TARGET/scripts/install.sh --unlink

First use in a project:
  python3 $TARGET/scripts/bap.py scaffold ./MyProject --layout protocol
  python3 $TARGET/scripts/bap.py status ./MyProject
EOF
