#!/usr/bin/env bash
#
# audit-performance.sh - Static code analysis for Next.js and React performance anti-patterns
#

set -eo pipefail

TARGET_DIR="${1:-.}"
echo "=========================================================="
echo " 🚀 Next.js & React Performance Static Audit"
echo " Target Directory: $TARGET_DIR"
echo "=========================================================="

WARNINGS=0

check_pattern() {
    local title="$1"
    local pattern="$2"
    local ext="$3"
    local advice="$4"

    echo ""
    echo "🔍 Checking: $title"
    
    # Run ripgrep if available, else fallback to grep
    if command -v rg >/dev/null 2>&1; then
        MATCHES=$(rg -n --glob "*.$ext" "$pattern" "$TARGET_DIR" 2>/dev/null || true)
    else
        MATCHES=$(grep -rn --include="*.$ext" -E "$pattern" "$TARGET_DIR" 2>/dev/null || true)
    fi

    if [ -n "$MATCHES" ]; then
        COUNT=$(echo "$MATCHES" | wc -l | tr -d ' ')
        echo "⚠️  Found $COUNT occurrences:"
        echo "$MATCHES" | head -n 5
        if [ "$COUNT" -gt 5 ]; then
            echo "   ... and $((COUNT - 5)) more."
        fi
        echo "💡 Advice: $advice"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "✅ None found."
    fi
}

# 1. Barrel icon imports (bloats bundle size)
check_pattern "Icon Barrel Imports (e.g. lucide-react, @tabler)" \
    "from ['\"](lucide-react|@tabler/icons-react)['\"]" \
    "{ts,tsx,js,jsx}" \
    "Import directly from subpaths (e.g., 'lucide-react/dist/esm/icons/search') to allow tree-shaking."

# 2. Standard <img> tag usage in Next.js projects
check_pattern "Standard <img> tags instead of next/image" \
    "<img\s" \
    "{tsx,jsx}" \
    "Use Next.js <Image /> component for automatic format conversion (WebP/AVIF), sizing, and lazy loading."

# 3. Sequential await inside loops
check_pattern "Sequential await inside loops" \
    "for\s*\(.*\)\s*\{[^}]*await\s+" \
    "{ts,tsx,js,jsx}" \
    "Replace sequential awaits with Promise.all() for concurrent network I/O."

# 4. 'use client' on page or layout files (CSR Anti-pattern: violates leaf-node rule)
check_pattern "'use client' directive in page or layout files" \
    "['\"]use client['\"]" \
    "{page.tsx,page.jsx,layout.tsx,layout.jsx}" \
    "Do NOT turn entire pages/layouts into Client Components. Keep pages as Server Components (RSC) and push 'use client' to leaf buttons/inputs."

# 5. useEffect used for data fetching (Network Waterfall Anti-pattern)
check_pattern "useEffect used for data fetching (fetch/axios)" \
    "useEffect\([^)]*(fetch\(|axios\.)" \
    "{ts,tsx,js,jsx}" \
    "Do not fetch data inside useEffect. In Next.js, fetch directly in async Server Components or use Server Actions."

# 6. useEffect used for derived state
check_pattern "useEffect with setState (Derived State Anti-pattern)" \
    "useEffect\([^)]*set[A-Z]" \
    "{ts,tsx,js,jsx}" \
    "Derive state directly during render or wrap in useMemo() instead of triggering extra renders via useEffect."

# 7. General useEffect audit count
check_pattern "Any useEffect usage (Verify against 'Goodbye useEffect' doctrine)" \
    "\buseEffect\(" \
    "{ts,tsx,js,jsx}" \
    "Audit all useEffect usages: 95% can be replaced by render computations, event handlers, or Server Components."

# 8. Missing passive scroll listeners
check_pattern "Scroll event listener without passive flag" \
    "addEventListener\(['\"](scroll|touchstart|touchmove)['\"][^,)]+\)" \
    "{ts,tsx,js,jsx}" \
    "Pass { passive: true } to prevent blocking the main thread during scrolling interactions."

# 9. TypeScript 'as any' assertions
check_pattern "TypeScript 'as any' bypass" \
    "as\s+any\b" \
    "{ts,tsx}" \
    "Eliminate 'as any'. Use 'unknown', runtime schemas (Zod), or proper type narrowing."

# 10. Optional-field bag state anti-pattern
check_pattern "Contradictory state bags (loading + error?)" \
    "loading:\s*boolean;[\s\n]*error\?:" \
    "{ts,tsx}" \
    "Model state with a discriminated union (status: 'loading' | 'error' | 'success') so impossible states cannot exist."

# 11. Direct DB queries in UI components (Separation of Concerns violation)
check_pattern "Direct database queries inside UI components" \
    "(prisma|db)\.[a-zA-Z]+\.(find|create|update|delete|query)" \
    "components/**/*.{tsx,jsx}" \
    "Separate concerns: extract database queries into dedicated Data Access Layer modules (e.g. lib/services/ or lib/dal/) instead of querying inside UI components."

# 12. Commented-out dead code
check_pattern "Commented-out dead code" \
    "^\s*//\s*(const|let|var|import|export|function)\s+" \
    "{ts,tsx,js,jsx}" \
    "Purge commented-out dead code. Rely on Git version history rather than cluttering active files."

# 13. Meaningless / Obvious comments
check_pattern "Meaningless / Obvious comments (narrating code)" \
    "//\s*(render\s+(component|button|ui)|handle\s+(click|submit)|fetch\s+(data|user)|set\s+state)\b" \
    "{ts,tsx,js,jsx}" \
    "Remove meaningless comments that merely restate what the code already says. Document the 'WHY', not the 'WHAT'."

# 14. Unslop: AI buzzwords in code comments
check_pattern "AI buzzwords in code comments (Unslop)" \
    "//.*\b(delve|testament|tapestry|crucial|pivotal|foster|game-changer)\b" \
    "{ts,tsx,js,jsx}" \
    "Apply Unslop: replace AI buzzwords with plain, concrete technical descriptions."

echo ""
echo "=========================================================="
if [ "$WARNINGS" -eq 0 ]; then
    echo "Success: No critical static performance or code quality anti-patterns detected."
else
    echo "Audit complete: Found $WARNINGS potential areas for performance or quality improvement."
fi
echo "=========================================================="
