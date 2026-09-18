#!/usr/bin/env bash
# ==============================================================================
# 🛡️ NestJS Backend Static Audit Script
# Scans NestJS codebases for architecture, security, performance, and style defects.
# ==============================================================================

set -euo pipefail

TARGET_DIR="."
STRICT_MODE=false

for arg in "$@"; do
  case "$arg" in
    --strict)
      STRICT_MODE=true
      ;;
    *)
      TARGET_DIR="$arg"
      ;;
  esac
done

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================================${NC}"
echo -e "${BLUE} 🛡️ NestJS Backend Architecture & Quality Static Audit     ${NC}"
echo -e "${BLUE} Target Directory: ${TARGET_DIR}                          ${NC}"
echo -e "${BLUE} Strict Mode:      ${STRICT_MODE}                         ${NC}"
echo -e "${BLUE}==========================================================${NC}"
echo ""

TOTAL_ISSUES=0
CRITICAL_ISSUES=0

run_check() {
  local title="$1"
  local pattern="$2"
  local includes="$3"
  local severity="$4"

  echo -e "${YELLOW}🔍 Checking: ${title}${NC}"
  
  local matches
  matches=$(grep -rEn --include="$includes" "$pattern" "$TARGET_DIR" 2>/dev/null || true)

  if [ -n "$matches" ]; then
    echo -e "${RED}❌ Found issues (${severity}):${NC}"
    echo "$matches" | head -n 10
    local count
    count=$(echo "$matches" | wc -l | tr -d ' ')
    if [ "$count" -gt 10 ]; then
      echo -e "${YELLOW}... and $((count - 10)) more instances.${NC}"
    fi
    TOTAL_ISSUES=$((TOTAL_ISSUES + count))
    if [ "$severity" = "CRITICAL" ]; then
      CRITICAL_ISSUES=$((CRITICAL_ISSUES + count))
    fi
  else
    echo -e "${GREEN}✅ None found.${NC}"
  fi
  echo ""
}

# 1. TypeScript 'as any' bypass
run_check "TypeScript 'as any' or ': any' bypass in services and controllers" \
  "(as\s+any|:\s*any\b)" \
  "*.ts" \
  "CRITICAL"

# 2. Direct database queries or ORM calls inside controllers
run_check "Direct DB/Prisma/TypeORM queries inside Controller files" \
  "(@Controller|export class .*Controller).*(\$queryRaw|this\.prisma\.|getRepository\(|\.createQueryBuilder)" \
  "*controller.ts" \
  "CRITICAL"

# 3. SQL injection via template string interpolation in raw queries
run_check "Potential SQL injection in raw query template literals" \
  "(\\\$queryRawUnsafe|\\.query)\([\"'\`][^\"'\`]*\\\$\{" \
  "*.ts" \
  "CRITICAL"

# 4. Service locator anti-pattern (ModuleRef dynamic resolution)
run_check "Service Locator anti-pattern (dynamic ModuleRef resolution)" \
  "(this\.moduleRef\.(get|resolve)|moduleRef\.(get|resolve))" \
  "*.ts" \
  "CRITICAL"

# 5. Unvalidated Body without DTO
run_check "Controller method receiving unvalidated raw body (@Body() body)" \
  "@Body\(\)\s+\w+:\s*(any|object|Record)" \
  "*controller.ts" \
  "HIGH"

# 6. Circular Dependency forwardRef usage
run_check "Circular dependency workaround (forwardRef usage)" \
  "forwardRef\(" \
  "*.ts" \
  "MEDIUM"

# 7. Contradictory boolean state bags
run_check "Contradictory boolean state bags ({ isLoading, isError, isSuccess })" \
  "(isLoading\?:?\s*boolean.*isError\?:?\s*boolean|isSuccess\?:?\s*boolean.*isError\?:?\s*boolean)" \
  "*.ts" \
  "HIGH"

# 8. Commented-out dead code
run_check "Commented-out dead code blocks" \
  "^\s*//\s*(const|let|var|await|return|this\.|import\s+|export\s+)" \
  "*.ts" \
  "MEDIUM"

# 9. Meaningless / Obvious comments narrating trivial syntax
run_check "Meaningless / Obvious comments narrating trivial code" \
  "//\s*(constructor|inject\s+|get\s+all|find\s+by\s+id|return\s+result|save\s+user)" \
  "*.ts" \
  "LOW"

# 10. AI Buzzwords in comments (Unslop)
run_check "AI buzzwords in code comments (Unslop compliance)" \
  "//.*(crucial|pivotal|delve|foster|testament|tapestry|landscape|enhance)" \
  "*.ts" \
  "LOW"

echo -e "${BLUE}==========================================================${NC}"
if [ "$TOTAL_ISSUES" -eq 0 ]; then
  echo -e "${GREEN}Success: No static NestJS anti-patterns detected.${NC}"
  echo -e "${BLUE}==========================================================${NC}"
  exit 0
else
  echo -e "${RED}Audit complete: ${TOTAL_ISSUES} potential issue(s) flagged (${CRITICAL_ISSUES} critical).${NC}"
  echo -e "${BLUE}==========================================================${NC}"
  if [ "$STRICT_MODE" = true ] && [ "$CRITICAL_ISSUES" -gt 0 ]; then
    echo -e "${RED}Strict mode failure: ${CRITICAL_ISSUES} critical issue(s) detected.${NC}"
    exit 1
  fi
  exit 0
fi
