# Vercel Runtime & Cost Optimization

Techniques for reducing compute spend, function invocations, and execution latency on Vercel.

---

## 1. Observability & Metric-First Investigation

Before making code changes for Vercel performance, inspect real metrics:
```bash
# Check usage metrics for current project
vercel usage

# Pull performance metrics (requires Observability Plus)
vercel metrics
```

### High Cost Drivers & Solutions
1. **Excessive Function Invocations:**
   - *Problem:* Every client navigation hits a serverless function because routes are dynamically rendered.
   - *Solution:* Convert dynamic pages to ISR (Incremental Static Regeneration) using `export const revalidate = 60` or Static Generation (`generateStaticParams`).
2. **High Fast Data Transfer (FDT):**
   - *Problem:* Returning large raw database payloads in Server Components or API responses.
   - *Solution:* Project and pick only required fields before JSON serialization.
3. **Long Compute Execution Time:**
   - *Problem:* Heavy database queries or sequential network calls in route handlers.
   - *Solution:* Add Prisma/ORM indexes, deduplicate calls with `React.cache()`, and enable Edge caching.

---

## 2. Next.js Caching Architecture on Vercel

```text
Request ──> Vercel Edge Cache (Data Cache / Full Route Cache)
                 ├── Hit: Return cached HTML/JSON (~10ms)
                 └── Miss: Invoke Serverless Function
                             ├── React.cache() (Deduplicate per-request)
                             └── Return Response + Update Edge Cache
```

### Next.js 15+ Cache Directives
- Use `use cache` for fine-grained function-level caching.
- Use `cacheTag()` and `revalidateTag()` for instant on-demand cache invalidation upon data mutation.
