# TypeScript Best Practices for Next.js & React

Type-system discipline and boundary validation principles for robust, high-performance Next.js and React applications.

---

## 🛑 DOCTRINE 3: TYPE-SYSTEM DISCIPLINE & BOUNDARY INTEGRITY

TypeScript is not just documentation; it is a compile-time correctness guarantee. In Next.js (RSC, Server Actions, Route Handlers), strict type boundaries prevent runtime crashes and data serialization leaks.

---

## 1. Discriminated Unions for Component States & Props

Never use bags of optional booleans (`isLoading?`, `isError?`, `data?`) that allow impossible states. Model state with a `kind` or `status` discriminant.

```tsx
// ❌ ANTI-PATTERN: Contradictory states can exist simultaneously
type State = {
  loading: boolean;
  error?: string;
  data?: User;
};

// ✅ BEST PRACTICE: Only legal states are constructable
type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: User }
  | { status: "error"; error: string };

function UserView({ state }: { state: State }) {
  switch (state.status) {
    case "idle":
      return null;
    case "loading":
      return <Skeleton />;
    case "success":
      return <Profile user={state.data} />;
    case "error":
      return <ErrorBanner message={state.error} />;
    default: {
      const _exhaustive: never = state;
      return _exhaustive;
    }
  }
}
```

### Mutually Exclusive Props

```tsx
// Link vs Button polymorphism modeled cleanly
type ButtonProps =
  | ({
      as?: "button";
      href?: never;
    } & React.ButtonHTMLAttributes<HTMLButtonElement>)
  | ({
      as: "link";
      href: string;
    } & React.AnchorHTMLAttributes<HTMLAnchorElement>);
```

---

## 2. Branded Types for Domain IDs & Sensitive Values

Brand primitive strings/numbers so IDs cannot be accidentally swapped or misused.

```typescript
export type UserId = string & { readonly __brand: "UserId" };
export type TeamId = string & { readonly __brand: "TeamId" };

export function parseUserId(raw: string): UserId {
  if (!raw.startsWith("usr_")) throw new Error(`Invalid UserId: ${raw}`);
  return raw as UserId;
}

// Compiler prevents passing TeamId to a function expecting UserId
function fetchUserPreferences(userId: UserId) {
  /* trusted */
}
```

---

## 3. Boundary Validation: Schemas Before Hand-Rolled Guards

All external data crossing into Next.js (Server Action inputs, Route Handler request bodies, `searchParams`, environment variables) must be validated with a runtime schema library (e.g. Zod). **Derive TypeScript types from schemas, never maintain duplicate interfaces.**

```typescript
// app/actions/create-post.ts
"use server";

import { z } from "zod";

const CreatePostSchema = z.object({
  title: z.string().min(3).max(100),
  content: z.string().min(10),
  tag: z.enum(["tech", "design", "biz"]),
});

export type CreatePostInput = z.infer<typeof CreatePostSchema>;

export async function createPostAction(input: unknown) {
  // 1. Validate at the boundary
  const parsed = CreatePostSchema.safeParse(input);
  if (!parsed.success) {
    return { success: false, errors: parsed.error.flatten().fieldErrors };
  }

  // 2. Downstream code trusts the verified type
  const { title, content, tag } = parsed.data;
  const post = await db.post.create({ data: { title, content, tag } });
  return { success: true, post };
}
```

---

## 4. `unknown` Over `any` & No Unearned `as` Casts

- **External data is `unknown`:** `JSON.parse()`, `req.json()`, `searchParams`, and 3rd-party SDK responses start as `unknown`.
- **No `as` assertions without validation:** Every `as Type` without validation is a latent runtime crash.
- **Narrowing Hierarchy:**
  1. Discriminated union switch
  2. `in` operator (`if ('error' in result) ...`)
  3. `typeof` / `instanceof`
  4. Runtime schema (`schema.parse()`)
  5. User-defined type guard (`function isX(val: unknown): val is X`)
  6. `as` cast (earned only after manual boundary check)

---

## 5. `satisfies` Over Type Annotations for Configurations

Use `satisfies` to validate object structure without widening literal types.

```typescript
// next.config.ts or Tailwind config
import type { NextConfig } from "next";

const nextConfig = {
  reactStrictMode: true,
  images: {
    formats: ["image/avif", "image/webp"],
  },
} satisfies NextConfig;

export default nextConfig;
```

---

## 6. Schema-Derived Types & Utility Types

Avoid declaring redundant interfaces when they can be derived from single sources of truth:

- `z.infer<typeof MySchema>`
- `ReturnType<typeof myAction>`
- `Awaited<ReturnType<typeof fetchUser>>`
- `React.ComponentProps<typeof Button>`
- `Pick<User, 'id' | 'name'>` / `Omit<User, 'hashedPassword'>`

---

## 7. Structured Logging over `console.log`

No `console.log` in shipped production Next.js code. Use structured telemetry with trace IDs for Server Components and Route Handlers.

---

## 8. Types as Constructions, Total Functions & Error Elimination

- **Types as Constructions:** Build types up from values that can only represent legal states. For example, represent a non-empty array as `[T, ...T[]]` instead of checking `.length > 0` at runtime. Represent a valid date range as `{ start: Date; durationMs: number }` instead of asserting `end >= start`.
- **Define Errors Out of Existence:** Prefer structural representations that make invalid combinations impossible over writing repetitive defensive handlers.
- **Strengthen Types at Partiality Points:** Whenever you feel compelled to write a defensive `?.` or throw an error for an unexpected case, push that requirement into the type signature so the function remains total and infallible.
