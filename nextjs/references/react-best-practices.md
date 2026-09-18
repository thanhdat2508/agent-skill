# React & Next.js Performance Engineering Guidelines

This reference compiles the 70 critical performance rules maintained by Vercel Engineering, categorized by priority and impact.

---

## 🛑 DOCTRINE 1: STRICTLY RESTRICT CLIENT-SIDE RENDERING (CSR)

Client-Side Rendering adds JavaScript bundle weight, causes hydration mismatches, delays LCP, and introduces unnecessary loading spinners. In modern Next.js (App Router), **Server Components (RSC) are the mandatory default**.

### 1. The Leaf-Node Rule for `'use client'`

Never put `'use client'` at the page, layout, or data-fetching level. Push `'use client'` down to the furthest leaf components in the DOM tree.

```tsx
// ❌ CRITICAL ANTI-PATTERN: Whole page marked as client component
"use client";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("/api/stats")
      .then((res) => res.json())
      .then(setData);
  }, []);

  return (
    <div>
      <Header />
      <StatsOverview data={data} />
      <InteractiveFilterButton />
    </div>
  );
}

// ✅ BEST PRACTICE: Server Component page, client boundary only at interactive leaf
// app/dashboard/page.tsx (Server Component by default)
export default async function DashboardPage() {
  const stats = await getStatsFromDatabase(); // Zero client JS! Direct DB query!

  return (
    <div>
      <Header />
      <StatsOverview data={stats} />
      {/* Only this tiny interactive button ships client JS */}
      <InteractiveFilterButton />
    </div>
  );
}
```

### 2. Passing Server Components as Children to Client Components

If a Client Component needs to wrap layout elements (e.g. an animated accordion or modal dialog), pass Server Components as `children` or props so the wrapped components remain rendered on the server with 0 client JS.

```tsx
// components/Modal.tsx
"use client";
export function Modal({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(true)}>Open</button>
      {open && <div className="dialog">{children}</div>}
    </div>
  );
}

// app/page.tsx (Server Component)
export default async function Page() {
  const data = await getHeavyData();
  return (
    <Modal>
      {/* HeavyServerList renders on server and sends 0 JS to client */}
      <HeavyServerList data={data} />
    </Modal>
  );
}
```

---

## 🛑 DOCTRINE 2: THE "GOODBYE useEffect" HANDBOOK

`useEffect` is an escape hatch for synchronizing with non-React systems. **95% of `useEffect` in legacy React codebases are bugs or anti-patterns** that harm performance by causing duplicate renders, layout thrashing, and uncoordinated waterfalls.

### Anti-Pattern 1: `useEffect` for Data Fetching

```tsx
// ❌ WRONG: Fetch-on-render waterfall, causes flash of empty state
function UserProfile({ id }: { id: string }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    fetch(`/api/user/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (!ignore) {
          setUser(data);
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, [id]);

  if (loading) return <Spinner />;
  return <div>{user.name}</div>;
}

// ✅ RIGHT (Next.js Server Component): Instant HTML, zero waterfall, zero client JS
async function UserProfile({ id }: { id: string }) {
  const user = await getUser(id);
  return <div>{user.name}</div>;
}

// ✅ RIGHT (If strictly in a client leaf): Use SWR or TanStack Query
function UserProfileClient({ id }: { id: string }) {
  const { data: user, isLoading } = useSWR(`/api/user/${id}`, fetcher);
  if (isLoading) return <Spinner />;
  return <div>{user.name}</div>;
}
```

### Anti-Pattern 2: `useEffect` for Derived State

```tsx
// ❌ WRONG: Causes an unnecessary extra re-render cycle
function Cart({ items }: { items: CartItem[] }) {
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setTotal(items.reduce((sum, item) => sum + item.price, 0));
  }, [items]);

  return <div>Total: ${total}</div>;
}

// ✅ RIGHT: Compute synchronously during render (or useMemo for heavy calculations)
function Cart({ items }: { items: CartItem[] }) {
  // Free, instantaneous, single-render computation
  const total = items.reduce((sum, item) => sum + item.price, 0);
  return <div>Total: ${total}</div>;
}
```

### Anti-Pattern 3: `useEffect` to Handle User Events

```tsx
// ❌ WRONG: Setting state just to trigger an effect
function BuyButton({ product }: { product: Product }) {
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (submitted) {
      postPurchase(product.id);
      showNotification("Purchased!");
    }
  }, [submitted]);

  return <button onClick={() => setSubmitted(true)}>Buy</button>;
}

// ✅ RIGHT: Execute actions directly in the event handler or Server Action
function BuyButton({ product }: { product: Product }) {
  const handleBuy = async () => {
    await buyProductAction(product.id); // Next.js Server Action
    showNotification("Purchased!");
  };

  return <button onClick={handleBuy}>Buy</button>;
}
```

### Anti-Pattern 4: `useEffect` to Reset State on Prop Change

```tsx
// ❌ WRONG: Flickers stale data from previous user before effect fires
function ProfileEditor({ userId }: { userId: string }) {
  const [comment, setComment] = useState("");

  useEffect(() => {
    setComment("");
  }, [userId]);

  return (
    <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
  );
}

// ✅ RIGHT: Pass key to force React to reset component state cleanly
function ProfilePage({ userId }: { userId: string }) {
  return <ProfileEditor key={userId} userId={userId} />;
}
```

### The ONLY Valid Uses of `useEffect`:

1. Subscribing to an external, non-React DOM API (e.g. `window.matchMedia`, `ResizeObserver`, custom Canvas animation loops) with a cleanup return function.
2. Initializing a browser-only imperative 3rd party SDK (e.g. Mapbox, Video player) that lacks a declarative React wrapper.

---

## 🛑 DOCTRINE 4: SEPARATION OF CONCERNS — THIN COMPONENTS & DATA ABSTRACTION

**Never dump data queries, mathematical transformations, business validations, and JSX rendering into a single monolithic component or page file.**

Components and pages should be **thin view orchestrators**. Their only job is to request data, delegate mutations, and render markup.

### 1. Server Data Logic: Extract to Data Access Layer (`lib/services/` or `lib/dal/`)

```tsx
// ❌ CRITICAL ANTI-PATTERN: Fat page mixing Prisma, calculations, and UI
// app/orders/[id]/page.tsx
export default async function OrderPage({ params }: { params: { id: string } }) {
  // Raw database queries mixed directly in page
  const order = await prisma.order.findUnique({
    where: { id: params.id },
    include: { items: true, customer: true, discounts: true },
  });

  if (!order) notFound();

  // Heavy business calculations & data transformations mixed in page
  const subtotal = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = subtotal * 0.08;
  const discountTotal = order.discounts
    .filter(d => d.active && new Date(d.expiresAt) > new Date())
    .reduce((sum, d) => sum + (d.type === 'PERCENT' ? subtotal * (d.value / 100) : d.value), 0);
  const total = Math.max(0, subtotal + tax - discountTotal);

  return (
    <div className="order-container">
      <h1>Order #{order.id}</h1>
      <div>Customer: {order.customer.name}</div>
      <div>Subtotal: ${subtotal.toFixed(2)}</div>
      <div>Tax: ${tax.toFixed(2)}</div>
      <div>Discount: -${discountTotal.toFixed(2)}</div>
      <h2>Final Total: ${total.toFixed(2)}</h2>
      {/* 150 more lines of JSX... */}
    </div>
  );
}

// ✅ BEST PRACTICE: Abstract data query & domain logic into lib/services/order.service.ts
// lib/services/order.service.ts
export async function getOrderSummary(orderId: string) {
  const order = await prisma.order.findUnique({
    where: { id: orderId },
    include: { items: true, customer: true, discounts: true },
  });
  if (!order) return null;

  const subtotal = calculateSubtotal(order.items);
  const tax = calculateTax(subtotal);
  const discount = calculateActiveDiscounts(order.discounts, subtotal);
  const total = Math.max(0, subtotal + tax - discount);

  return { order, subtotal, tax, discount, total };
}

// app/orders/[id]/page.tsx (Clean, thin orchestrator: ~20 lines!)
import { getOrderSummary } from '@/lib/services/order.service';
import { OrderSummaryCard } from '@/components/orders/OrderSummaryCard';

export default async function OrderPage({ params }: { params: { id: string } }) {
  const summary = await getOrderSummary(params.id);
  if (!summary) notFound();

  return (
    <main className="max-w-4xl mx-auto p-6">
      <OrderSummaryCard summary={summary} />
    </main>
  );
}
```

### 2. Client Interactive Logic: Extract to Custom Hooks (`hooks/`)

When a Client Component requires stateful filtering, pagination, search debouncing, or form handling, **extract that state machine into a custom hook**. The component itself should only wire up the UI.

```tsx
// ❌ ANTI-PATTERN: Fat client component with 100 lines of state management
'use client';
export function ProductCatalog({ initialProducts }: { initialProducts: Product[] }) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc'>('price-asc');
  const [currentPage, setCurrentPage] = useState(1);
  // 50 lines of filtering, debouncing, sorting, and pagination logic inline...
  // Followed by 100 lines of table JSX...
}

// ✅ BEST PRACTICE: Extract logic to custom hook
// hooks/useProductFilters.ts
export function useProductFilters(products: Product[]) {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState<'price-asc' | 'price-desc'>('price-asc');
  const [page, setPage] = useState(1);

  const filteredProducts = useMemo(() => {
    return filterAndSortProducts(products, { search, category, sortBy });
  }, [products, search, category, sortBy]);

  const paginatedItems = useMemo(() => {
    return paginate(filteredProducts, page, 20);
  }, [filteredProducts, page]);

  return {
    search, setSearch,
    category, setCategory,
    sortBy, setSortBy,
    page, setPage,
    items: paginatedItems,
    totalCount: filteredProducts.length,
  };
}

// components/ProductCatalog.tsx (Thin presentational component)
'use client';
import { useProductFilters } from '@/hooks/useProductFilters';

export function ProductCatalog({ initialProducts }: { initialProducts: Product[] }) {
  const { search, setSearch, items, page, setPage } = useProductFilters(initialProducts);

  return (
    <section>
      <SearchBar value={search} onChange={setSearch} />
      <ProductGrid items={items} />
      <Pagination current={page} onPageChange={setPage} />
    </section>
  );
}
```

---

## 🛑 DOCTRINE 5: CODE DOCUMENTATION INTEGRITY — NO MEANINGLESS COMMENTS, HIGH-SIGNAL & FRESH ONLY

**Comments must never state what the code already clearly says. If a comment exists, it must provide high-signal context and must be completely accurate and up-to-date.**

### 1. Banned: Meaningless, Obvious & Redundant Comments

Do not add noise that clutters the screen and wastes LLM token context.

```tsx
// ❌ CRITICAL ANTI-PATTERN: Obvious noise restating the code
// Define user state
const [user, setUser] = useState<User | null>(null);

// Effect to fetch user data on mount
useEffect(() => {
  getUser();
}, []);

// Handle button click
const handleClick = () => {
  submitForm();
};

// Render component
return (
  <div>
    {/* User name */}
    <h1>{user.name}</h1>
    {/* Submit button */}
    <button onClick={handleClick}>Submit</button>
  </div>
);

// ✅ BEST PRACTICE: Self-documenting code with zero noise
const [user, setUser] = useState<User | null>(null);
const handleSubmit = () => submitForm();

return (
  <div>
    <h1>{user.name}</h1>
    <button onClick={handleSubmit}>Submit</button>
  </div>
);
```

### 2. Banned: Commented-Out Dead Code

Never leave dead or superseded code blocks in the repository. Trust Git version control for history.

```tsx
// ❌ WRONG: Zombie code left behind
// const discountedTotal = calculateLegacyDiscount(items);
// if (isHoliday) {
//   return <HolidayPromo items={items} />;
// }
return <StandardCheckout items={items} />;

// ✅ RIGHT: Clean, active code only
return <StandardCheckout items={items} />;
```

### 3. Allowed & Encouraged: High-Value Comments Explaining the "WHY"

Use comments exclusively when the code itself cannot express the hidden rationale:

```tsx
// ✅ EXCELLENT: Explains a non-obvious browser quirk or performance trade-off
// Workaround for Safari 16.4 flexbox height calculation bug:
// Without min-height: 0, Safari collapses child overflow-y containers inside nested flex columns.
containerRef.current.style.minHeight = '0px';

// ✅ EXCELLENT: Explains an architectural decision or business rule
// Business Rule (Policy #3.4): Enterprise tenants require cryptographic audit hashing.
// We defer this non-blocking calculation via after() to keep TTFB below 80ms.
after(async () => {
  await recordAuditHash(payload);
});
```

### 4. Freshness Mandate: Stale Comments Are Bugs

An outdated comment is more dangerous than no comment because it misleads future maintainers and AI coding assistants.
- **Whenever you modify a function's behavior, parameters, or return shape, you MUST update or delete its existing comments.**
- If a comment contradicts the code, treat it as a **Severity 1 defect** and resolve it immediately.

---

## Priority 1: Eliminating Waterfalls (CRITICAL)

Unnecessary sequential `await` calls multiply latency across networks.

### `async-parallel` - Use Promise.all() for independent operations

```typescript
// ❌ Bad: Sequential waterfall (takes timeA + timeB)
const user = await fetchUser(id);
const posts = await fetchPosts(id);

// ✅ Good: Concurrent execution (takes max(timeA, timeB))
const [user, posts] = await Promise.all([fetchUser(id), fetchPosts(id)]);
```

### `async-cheap-condition-before-await` - Check cheap condition first

```typescript
// ❌ Bad: Awaiting remote flag before checking local condition
const isFeatureEnabled = await checkFeatureFlag("new-ui");
if (!user.isPremium) return null;

// ✅ Good: Test cheap local memory/prop condition before awaiting remote service
if (!user.isPremium) return null;
const isFeatureEnabled = await checkFeatureFlag("new-ui");
```

### `async-defer-await` - Move await into the branch where needed

```typescript
// ❌ Bad: Awaits unconditionally even if cached in local memory
const session = await getSession();
if (memoryCache.has(key)) return memoryCache.get(key);

// ✅ Good: Only await when cache misses
if (memoryCache.has(key)) return memoryCache.get(key);
const session = await getSession();
```

### `async-suspense-boundaries` - Stream slow components

```tsx
// ❌ Bad: Blocking the entire page render while waiting for slow recommendations
export default async function Page() {
  const feed = await getFeed();
  const recommendations = await getSlowRecommendations(); // blocks entire HTML
  return (
    <div>
      <Feed data={feed} />
      <Recs data={recommendations} />
    </div>
  );
}

// ✅ Good: Stream the slow section inside Suspense
export default async function Page() {
  const feed = await getFeed();
  return (
    <div>
      <Feed data={feed} />
      <Suspense fallback={<RecsSkeleton />}>
        <SlowRecommendations />
      </Suspense>
    </div>
  );
}
```

---

## Priority 2: Bundle Size Optimization (CRITICAL)

### `bundle-barrel-imports` - Avoid barrel files

```typescript
// ❌ Bad: Pulls in hundreds of icon modules and bloats build/chunk size
import { Search, ChevronDown, Check } from "lucide-react";

// ✅ Good: Direct path imports allow precise tree-shaking
import Search from "lucide-react/dist/esm/icons/search";
import ChevronDown from "lucide-react/dist/esm/icons/chevron-down";
import Check from "lucide-react/dist/esm/icons/check";
```

### `bundle-dynamic-imports` - Use next/dynamic for heavy client components

```tsx
import dynamic from "next/dynamic";

// ❌ Bad: Statically bundling 500KB heavy chart library into main page bundle
// import HeavyChart from '@/components/HeavyChart';

// ✅ Good: Lazy load only when rendered on client
const HeavyChart = dynamic(() => import("@/components/HeavyChart"), {
  ssr: false,
  loading: () => <ChartSkeleton />,
});
```

### `bundle-defer-third-party` - Defer non-critical scripts

Use `next/script` with appropriate strategy:

```tsx
import Script from "next/script";

<Script
  src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
  strategy="lazyOnload" // Loads during browser idle time
/>;
```

---

## Priority 3: Server-Side Performance (HIGH)

### `server-cache-react` - Per-request deduplication with React.cache()

```typescript
import { cache } from "react";

// Multiple components calling getCurrentUser() in the same request share 1 execution
export const getCurrentUser = cache(async (token: string) => {
  return await db.user.findUnique({ where: { token } });
});
```

### `server-serialization` - Minimize payload passed to Client Components

```tsx
// ❌ Bad: Passing full 50-field database record across RSC boundary
export default async function ServerPage() {
  const user = await db.user.findUnique(...);
  return <ClientUserProfile user={user} />;
}

// ✅ Good: Select only the required fields
export default async function ServerPage() {
  const user = await db.user.findUnique({
    select: { id: true, name: true, avatarUrl: true },
  });
  return <ClientUserProfile id={user.id} name={user.name} avatarUrl={user.avatarUrl} />;
}
```

### `server-after-nonblocking` - Use after() for background tasks (Next.js 15+)

```typescript
import { after } from "next/server";

export async function POST(req: Request) {
  const result = await processOrder(req);

  // Non-blocking: logs and analytics run without delaying the response
  after(async () => {
    await sendAuditLog(result);
    await trackAnalyticsEvent("order_completed");
  });

  return Response.json(result);
}
```

---

## Priority 4: Re-render & Rendering Performance (MEDIUM)

### `rerender-derived-state-no-effect` - Compute state during render

```typescript
// ❌ Bad: Triggering a second render cycle via useEffect
const [items, setItems] = useState([]);
const [filteredItems, setFilteredItems] = useState([]);
useEffect(() => {
  setFilteredItems(items.filter((i) => i.active));
}, [items]);

// ✅ Good: Derive during render (optionally wrapped in useMemo if calculation is heavy)
const filteredItems = useMemo(() => items.filter((i) => i.active), [items]);
```

### `rerender-functional-setstate` - Stable callbacks

```typescript
// ❌ Bad: handler must change whenever count changes
const increment = useCallback(() => setCount(count + 1), [count]);

// ✅ Good: callback identity remains permanent
const increment = useCallback(() => setCount((c) => c + 1), []);
```

### `rendering-content-visibility` - CSS content-visibility for long lists

```css
.list-item-card {
  content-visibility: auto;
  contain-intrinsic-size: 0 120px; /* Estimates height before rendering */
}
```

_Allows the browser to skip rendering calculations for items off-screen until scrolled near._

### `rendering-hydration-no-flicker` - Flash of Unstyled Theme prevention

```html
<head>
  <script
    dangerouslySetInnerHTML={{
      __html: `
        try {
          const theme = localStorage.getItem('theme') || 'system';
          if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            document.documentElement.classList.add('dark');
          }
        } catch (_) {}
      `,
    }}
  />
</head>
```
