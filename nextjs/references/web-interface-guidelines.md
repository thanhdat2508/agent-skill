# Web Interface Guidelines & UI/UX Standards

Standards derived from Vercel Labs Web Interface Guidelines for consistent, accessible, and high-performance UI interactions.

---

## 1. Interaction & Feedback

- **Interactive States:** Every interactive element (`<button>`, `<a>`, custom clickable cards) must provide clear visual states for `:hover`, `:focus-visible`, `:active`, and `:disabled`.
- **Focus Rings:** Never remove `outline: none` without providing an accessible `:focus-visible` replacement.
- **Button Feedback:** Disable double-clicking during async mutations (`isPending` / `isSubmitting`) while maintaining accessible labels.
- **Touch Target Size:** Interactive elements on touch devices should meet minimum bounding box dimensions (minimum 44x44px).

---

## 2. Layout & Typography

- **Fluid Typography:** Use modern CSS `clamp()` for responsive font sizing without layout snapping.
- **Safe Area Insets:** Account for mobile notches using `env(safe-area-inset-top)` and `env(safe-area-inset-bottom)`.
- **Scroll Containment:** Prevent unwanted body bounce using `overscroll-behavior: contain` inside modal overlays and side drawers.
- **Consistent Spacing Scale:** Rely strictly on design system tokens (e.g. Tailwind spacing scale `4`, `8`, `12`, `16`, `24`, `32`).
