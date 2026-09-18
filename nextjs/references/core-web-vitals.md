# Core Web Vitals (LCP, INP, CLS) Deep Playbook

Target Google's 75th percentile thresholds for page experience and SEO ranking.

---

## The Thresholds

| Metric | Full Name | Good | Needs Work | Poor | Primary Focus |
|:---|:---|:---:|:---:|:---:|:---|
| **LCP** | Largest Contentful Paint | **≤ 2.5s** | 2.5s – 4.0s | > 4.0s | Loading Speed of Hero Content |
| **INP** | Interaction to Next Paint | **≤ 200ms** | 200ms – 500ms | > 500ms | Main Thread Responsiveness |
| **CLS** | Cumulative Layout Shift | **≤ 0.1** | 0.1 – 0.25 | > 0.25 | Visual Bounding Stability |

---

## 1. LCP (Largest Contentful Paint) Optimization

### Step 1: Identify the LCP Element
Run this in browser DevTools Console:
```javascript
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP Element:', lastEntry.element);
  console.log('LCP Render Time:', `${lastEntry.startTime.toFixed(2)}ms`);
  console.log('LCP Resource URL:', lastEntry.url);
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

### Step 2: High-Priority Image Preload
When the LCP element is an image:
```html
<link rel="preload" href="/hero.webp" as="image" fetchpriority="high" />
```
In Next.js:
```tsx
import Image from 'next/image';

<Image
  src="/hero.webp"
  alt="Hero banner"
  width={1200}
  height={600}
  priority // High fetchpriority + preloads link in head
  sizes="(max-width: 768px) 100vw, 1200px"
/>
```

### Step 3: Speculation Rules API for Instant Navigations
Eliminate LCP on internal navigations by prerendering target routes:
```html
<script type="speculationrules">
{
  "prerender": [
    {
      "where": {
        "and": [
          { "href_matches": "/*" },
          { "not": { "href_matches": "/api/*" } },
          { "not": { "href_matches": "/logout" } }
        ]
      },
      "eagerness": "moderate"
    }
  ]
}
</script>
```
*`moderate` triggers after ~200ms hover on a link, delivering near 0ms LCP on navigation.*

---

## 2. INP (Interaction to Next Paint) Optimization

### Step 1: Yielding the Main Thread
Break up tasks longer than 50ms to let the browser paint user input feedback:
```typescript
export async function yieldToMain() {
  if ('scheduler' in window && 'yield' in (window as any).scheduler) {
    return await (window as any).scheduler.yield();
  }
  return new Promise((resolve) => setTimeout(resolve, 0));
}

// Example usage in an event handler:
async function handleFilterChange(items: Item[]) {
  // 1. Immediately give visual feedback
  setIsLoading(true);
  await yieldToMain();

  // 2. Perform chunked calculations
  for (let i = 0; i < items.length; i += 1000) {
    processBatch(items.slice(i, i + 1000));
    await yieldToMain(); // Yield back to browser to prevent freezing
  }

  setIsLoading(false);
}
```

### Step 2: React Transitions (`startTransition`)
Keep inputs interactive while filtering heavy lists:
```tsx
import { useState, useTransition } from 'react';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const [filteredList, setFilteredList] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    // Urgent: updates input field immediately
    setQuery(e.target.value);

    // Non-urgent: deferred update does not block keyboard input
    startTransition(() => {
      setFilteredList(performHeavyFilter(e.target.value));
    });
  };

  return <input value={query} onChange={handleChange} />;
}
```

---

## 3. CLS (Cumulative Layout Shift) Optimization

### Fix 1: Explicit Dimensions & Aspect Ratio
Always prevent DOM reflow by declaring sizing upfront:
```css
/* Responsive container preserving 16:9 ratio */
.video-wrapper {
  width: 100%;
  aspect-ratio: 16 / 9;
}
```

### Fix 2: Font Fallback Metric Overrides
Prevent layout jumping when web fonts swap in:
```css
@font-face {
  font-family: 'CustomFont-Fallback';
  src: local('Arial');
  ascent-override: 95%;
  descent-override: 25%;
  line-gap-override: 0%;
  size-adjust: 102%;
}

body {
  font-family: 'CustomFont', 'CustomFont-Fallback', sans-serif;
}
```

### Fix 3: Dynamic Banners and Ad Units
Reserve height in CSS for asynchronous content:
```css
.ad-slot-header {
  min-height: 90px; /* Never let container collapse to 0px before ad loads */
  display: block;
}
```
