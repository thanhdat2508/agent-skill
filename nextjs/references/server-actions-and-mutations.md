# Server Actions, Mutations & Next.js 15 Async Standards

Modern architecture standards for handling server mutations, form state transitions, and Next.js 15 async contracts.

---

## 1. Next.js 15 Breaking Change: Async Request APIs

In Next.js 15, runtime request headers, cookies, and route parameters are asynchronous promises. Synchronous access is deprecated and logs runtime errors.

### Page and Layout Route Parameters

```tsx
// ❌ Deprecated in Next.js 15: Synchronous params access
interface PageProps {
  params: { id: string };
  searchParams: { filter?: string };
}
export default function UserPage({ params, searchParams }: PageProps) {
  const userId = params.id; // Warning / error in Next.js 15!
  return <div>{userId}</div>;
}

// ✅ Next.js 15 Standard: Await params and searchParams
interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ filter?: string }>;
}
export default async function UserPage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const { filter } = await searchParams;
  return <div>User: {id} (Filter: {filter})</div>;
}
```

### Cookies & Headers

```tsx
// ❌ Deprecated: Synchronous cookies() / headers()
import { cookies, headers } from "next/headers";
const cookieStore = cookies();
const token = cookieStore.get("token");

// ✅ Next.js 15 Standard: Await cookies() and headers()
import { cookies, headers } from "next/headers";
const cookieStore = await cookies();
const token = cookieStore.get("token")?.value;
const headersList = await headers();
const userAgent = headersList.get("user-agent");
```

---

## 2. Server Actions Contract & Error Protocol

Server Actions must not throw unhandled exceptions for domain or validation errors. Throwing causes generic HTTP 500 error boundaries and destroys form state.

### Standard Action Return Shape

```typescript
export type ActionResult<T = void> =
  | { success: true; data: T }
  | { success: false; errors: Record<string, string[]>; message?: string };
```

### Robust Server Action Pattern

```typescript
// app/actions/create-order.ts
"use server";

import { z } from "zod";
import { revalidateTag } from "next/cache";
import { redirect } from "next/navigation";
import type { ActionResult } from "@/types/actions";

const CreateOrderSchema = z.object({
  productId: z.string().min(1, "Product is required"),
  quantity: z.coerce.number().int().positive("Quantity must be greater than 0"),
});

export async function createOrderAction(
  prevState: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  // 1. Parse boundary safely
  const parsed = CreateOrderSchema.safeParse({
    productId: formData.get("productId"),
    quantity: formData.get("quantity"),
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors,
      message: "Validation failed. Please correct input.",
    };
  }

  // 2. Perform mutation
  let orderId: string;
  try {
    const order = await db.orders.create({ data: parsed.data });
    orderId = order.id;
    revalidateTag("orders");
  } catch (error) {
    return {
      success: false,
      errors: {},
      message: "Failed to place order due to a database error.",
    };
  }

  // 3. Redirect outside of try-catch block!
  redirect(`/orders/${orderId}`);
}
```

> [!CAUTION]
> **The `redirect()` in `try...catch` Trap:**
> `redirect()` works by throwing a special `NEXT_REDIRECT` error. If you call `redirect()` inside a `try...catch` block without rethrowing it, the catch block intercepts it and fails to perform the HTTP redirection. Either call `redirect()` outside `try...catch`, or rethrow if `isRedirectError(error)` is true.

---

## 3. React 19 / Modern Form State: `useActionState` & `useOptimistic`

React 19 replaces `useFormState` with `useActionState`.

```tsx
// components/OrderForm.tsx
"use client";

import { useActionState, useOptimistic } from "react";
import { createOrderAction } from "@/app/actions/create-order";

export function OrderForm({ initialOrders }: { initialOrders: Order[] }) {
  const [state, formAction, isPending] = useActionState(createOrderAction, null);

  const [optimisticOrders, addOptimisticOrder] = useOptimistic(
    initialOrders,
    (state, newOrder: Order) => [newOrder, ...state]
  );

  return (
    <form action={formAction}>
      <input name="productId" placeholder="Product ID" required />
      {state?.errors?.productId && (
        <span className="text-red-500">{state.errors.productId[0]}</span>
      )}

      <input name="quantity" type="number" defaultValue="1" required />
      {state?.errors?.quantity && (
        <span className="text-red-500">{state.errors.quantity[0]}</span>
      )}

      <button type="submit" disabled={isPending}>
        {isPending ? "Submitting..." : "Place Order"}
      </button>

      {state?.message && !state.success && (
        <p className="text-red-600 mt-2">{state.message}</p>
      )}
    </form>
  );
}
```

---

## 4. Revalidation & Caching Strategy

- **`revalidatePath(path, type)`**: Use `revalidatePath('/products', 'page')` when a single route needs fresh HTML.
- **`revalidateTag(tag)`**: Preferred for data-driven applications. Tag `fetch(url, { next: { tags: ['products'] } })` or `unstable_cache` calls with semantic tags and invalidate with `revalidateTag('products')`.
