# TypeScript Best Practices for NestJS Backend Engineering

Type-system discipline, boundary validation, and compile-time correctness guidelines for enterprise NestJS applications.

---

## 1. Discriminated Unions for Domain Models & API Envelopes

Never use loose bags of optional booleans (`isSuccess?`, `error?`, `data?`) that allow invalid states to compile. Model domain states and API response envelopes with explicit discriminants.

```typescript
// ❌ ANTI-PATTERN: Contradictory states can compile simultaneously
type ServiceResult<T> = {
  success: boolean;
  data?: T;
  errorMessage?: string;
  errorCode?: string;
};

// ✅ BEST PRACTICE: Only valid states can be constructed
type ServiceResult<T> =
  | { success: true; data: T }
  | { success: false; error: { code: string; message: string } };

export function handleResult<T>(result: ServiceResult<T>) {
  if (result.success) {
    return { status: 200, payload: result.data };
  }
  return { status: 400, error: result.error.message };
}
```

---

## 2. Branded Types for Domain Identifiers

Primitive strings (`string`) for entity IDs cause catastrophic bugs when parameters are accidentally swapped. Brand entity IDs to prevent cross-assignment at compile time.

```typescript
// Define branded types
export type UserId = string & { readonly __brand: "UserId" };
export type OrderId = string & { readonly __brand: "OrderId" };
export type TenantId = string & { readonly __brand: "TenantId" };

// Factory functions that validate format
export function toUserId(raw: string): UserId {
  if (!raw || raw.length < 8) {
    throw new Error("Invalid UserId format");
  }
  return raw as UserId;
}

// ❌ COMPILE ERROR: Prevents accidental parameter swaps
function processOrder(userId: UserId, orderId: OrderId) {
  /* ... */
}

const userId = toUserId("usr_123");
const orderId = "ord_456" as OrderId;

// processOrder(orderId, userId); // 💥 Type error: Type 'OrderId' is not assignable to type 'UserId'
processOrder(userId, orderId); // ✅ Correct
```

---

## 3. Strict Boundary Validation for DTOs

Every incoming HTTP request, WebSocket event, or message queue payload must be validated at the boundary before entering business services.

```typescript
import { IsString, IsEmail, IsNotEmpty, MinLength } from "class-validator";
import { Transform } from "class-transformer";

export class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  @Transform(({ value }) => value?.trim().toLowerCase())
  readonly email: string;

  @IsString()
  @MinLength(8)
  readonly password: string;
}
```

In `main.ts`, enable strict global validation:

```typescript
app.useGlobalPipes(
  new ValidationPipe({
    whitelist: true, // Strip properties without decorators
    forbidNonWhitelisted: true, // Throw error if unmapped properties are passed
    transform: true, // Automatically transform payloads to DTO instances
  }),
);
```

---

## 4. Types as Constructions, Not Restrictions

Construct types up from valid primitives so illegal values cannot be constructed:

```typescript
// ❌ ANTI-PATTERN: Allows end < start
type TimeRange = {
  start: Date;
  end: Date;
};

// ✅ BEST PRACTICE: Impossibility of negative durations guaranteed by construction
type TimeRange = {
  readonly start: Date;
  readonly durationMs: number; // Must be >= 0
};
```

---

## 5. Type-Safe Dependency Injection Tokens

Avoid injecting dependencies using magic strings (`@Inject('USER_REPO')`). Use `Symbol` or typed tokens to preserve type safety across the NestJS dependency injection container:

```typescript
// tokens.ts
export const USER_REPOSITORY_TOKEN = Symbol("USER_REPOSITORY_TOKEN");

export interface IUserRepository {
  findById(id: UserId): Promise<UserEntity | null>;
  save(user: UserEntity): Promise<void>;
}

// user.service.ts
@Injectable()
export class UserService {
  constructor(
    @Inject(USER_REPOSITORY_TOKEN)
    private readonly userRepo: IUserRepository,
  ) {}
}
```

---

## 6. Zero `as any` Policy & External Untyped Payloads

External data (webhooks, message queues, third-party APIs) must be typed as `unknown` and narrowed using schemas or type guards before consumption:

```typescript
// ❌ ANTI-PATTERN: Bypassing type checking
async handleWebhook(payload: any) {
  this.processPayment(payload.data.id);
}

// ✅ BEST PRACTICE: Validate unknown payload before casting
import { z } from 'zod';

const WebhookSchema = z.object({
  id: z.string(),
  amount: z.number().positive(),
  status: z.enum(['paid', 'failed']),
});

type WebhookPayload = z.infer<typeof WebhookSchema>;

async handleWebhook(rawPayload: unknown) {
  const result = WebhookSchema.safeParse(rawPayload);
  if (!result.success) {
    throw new BadRequestException('Malformed webhook payload');
  }
  await this.processPayment(result.data.id, result.data.amount);
}
```

---

## 7. Exhaustive Matching on Sum Types

Always enforce compile-time exhaustiveness when switching over domain variants:

```typescript
type OrderStatus = "pending" | "processing" | "shipped" | "delivered";

export function getStatusLabel(status: OrderStatus): string {
  switch (status) {
    case "pending":
      return "Pending Payment";
    case "processing":
      return "Processing Order";
    case "shipped":
      return "In Transit";
    case "delivered":
      return "Delivered";
    default: {
      // 💥 Compile error if a new variant is added to OrderStatus without a case arm!
      const _exhaustiveCheck: never = status;
      return _exhaustiveCheck;
    }
  }
}
```
