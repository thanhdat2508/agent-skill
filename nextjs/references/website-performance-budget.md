# Website Performance Budget & Critical Rendering Path

Guidelines for asset loading, compression, and network architecture.

---

## 1. Critical Rendering Path

### Time to First Byte (TTFB < 800ms)
- **Edge Deployment:** Deploy serverless functions and SSR handlers geographically close to users (Cloudflare Workers, Vercel Edge, AWS CloudFront).
- **Early Hints (HTTP 103):** Send critical asset preload hints before the full HTML response is computed:
  ```http
  HTTP/1.1 103 Early Hints
  Link: </fonts/inter.woff2>; rel=preload; as=font; type="font/woff2"; crossorigin
  Link: </hero.webp>; rel=preload; as=image
  ```

### Resource Hints Checklist
```html
<!-- 1. DNS Pre-resolve and TLS handshake for external APIs -->
<link rel="preconnect" href="https://api.yourservice.com" />
<link rel="preconnect" href="https://cdn.example.com" crossorigin />

<!-- 2. Preload only true above-the-fold critical assets -->
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin />
```

---

## 2. Asset Compression & Delivery Standards

### Text Assets (HTML / JS / CSS)
- **Brotli (`.br`):** Always enable Brotli compression (15-25% smaller than gzip at comparable compression levels).
- **Purge Unused CSS:** In Tailwind CSS, ensure content paths strictly match only used template files.
- **Avoid CSS `@import`:** `@import` causes sequential network requests; bundle styles or link directly in HTML.

### Images & Media
- **Formats:** AVIF (highest compression) > WebP (broad fallback) > SVG (vectors) > JPEG/PNG.
- **Responsive Images:** Use `srcset` and `sizes` to avoid delivering 4K images to mobile screens.
- **Lazy Loading:** Apply `loading="lazy"` to all images below the initial viewport.

---

## 3. Performance Budget Monitoring Table

| Resource | Hard Limit | Alarm Trigger | Resolution Action |
|:---|:---:|:---:|:---|
| **Total Page Weight** | 1.5 MB | > 1.2 MB | Audit uncompressed assets & 3rd-party tags |
| **JS Bundle (gzip)** | 300 KB | > 250 KB | Split code via dynamic imports, check bundle visualizer |
| **CSS (gzip)** | 100 KB | > 80 KB | Extract critical CSS, eliminate unused styles |
| **Image (Above fold)** | 500 KB | > 400 KB | Convert to WebP/AVIF, resize source dimensions |
| **Custom Web Fonts** | 100 KB | > 80 KB | Subset to Latin-only characters, use WOFF2 |
| **3rd-Party Scripts** | 200 KB | > 150 KB | Audit Tag Manager, replace heavy SDKs with lightweight endpoints |
