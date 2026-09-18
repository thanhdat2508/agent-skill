# Backend Verification & Testing Playbook for NestJS

Guidelines for generating, executing, and maintaining verification skills and test suites for NestJS backends.

---

## 1. Interviewing the NestJS Repository

When establishing a verification harness for a NestJS application, interview the repository systematically:

1. **Surface:**
   - What interfaces does the backend expose?
     - REST endpoints (e.g. `/api/v1/...`)
     - GraphQL schemas (queries, mutations, subscriptions)
     - gRPC microservice handlers
     - Message queue listeners (RabbitMQ, Kafka, BullMQ)
     - WebSocket gateways (`@WebSocketGateway()`)

2. **Run:**
   - How does the application start locally?
   - Identify package scripts (`pnpm start:dev`, `npm run start:dev`).
   - Identify dependent services in `docker-compose.yml` (PostgreSQL, MySQL, Redis, MinIO).
   - Locate database migration commands (`pnpm prisma migrate deploy`, `npm run typeorm migration:run`).
   - Locate test seed scripts (`pnpm prisma db seed`).

3. **Drive:**
   - How can an automated agent drive the backend?
   - **Primary Harness:** Supertest (`request(app.getHttpServer())`) for HTTP/REST.
   - **Secondary Harness:** Custom test client or curl scripts for microservices and queues.

4. **Observe:**
   - What evidence proves the feature works?
   - HTTP response status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`).
   - Response body JSON schemas.
   - Database table state changes (asserting rows in PostgreSQL/MySQL).
   - Redis cache keys and TTLs.
   - Structured JSON log entries.

5. **Isolate:**
   - Run tests against an isolated test database (e.g. `test_db` or Docker container on distinct port).
   - Use transactional test rollbacks or automated database truncation between test suites.

---

## 2. Pre-Flight Doctor Checks

Before running any test pass or driving live endpoints, execute a non-destructive doctor check:

```typescript
// test/doctor.ts
export async function doctorCheck(app: INestApplication) {
  // 1. Check Database connection
  const prisma = app.get(PrismaService);
  await prisma.$queryRaw`SELECT 1`;

  // 2. Check Redis connection
  const redis = app.get(REDIS_CLIENT);
  const pong = await redis.ping();
  if (pong !== 'PONG') throw new Error('Redis ping failed');

  // 3. Verify application port liveness
  const httpServer = app.getHttpServer();
  if (!httpServer) throw new Error('HTTP server is not initialized');
}
```

---

## 3. Supertest Behavioral Testing Standard

Assert observable HTTP behavior and literal response values, not internal mock calls:

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('UsersController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }));
    await app.init();
  });

  afterAll(async () => {
    await app.close(); // Clean up connections to prevent hanging processes
  });

  it('POST /api/v1/users creates a new user and returns 201', async () => {
    const payload = {
      email: 'alex@example.com',
      password: 'StrongPassword123!',
    };

    const response = await request(app.getHttpServer())
      .post('/api/v1/users')
      .send(payload)
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'alex@example.com',
    });
    expect(response.body).not.toHaveProperty('password'); // Ensure password was sanitized
  });

  it('POST /api/v1/users fails with 400 when invalid email is provided', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/users')
      .send({ email: 'invalid-email', password: 'Short' })
      .expect(400);

    expect(response.body.message).toContain('email must be an email');
  });
});
```

---

## 4. Upkeep Loop: Maintaining Feature Maps & Preventing Drift

A backend feature map rots when endpoints or DTOs change without documentation updates.
- **Source Inspection Waves:** Concurrently analyze controller decorators and DTOs to detect undocumented routes or changed validation rules.
- **Live Driving Passes:** Re-run Supertest E2E suites against each documented feature.
- **Clean Residue:** Guarantee test database tables are truncated and Redis keys are cleared after each run.
- **Clear Outcome Reporting:** Classify upkeep runs as `clean` (everything in sync), `changed` (documentation/test harness corrected), or `blocked` (real server defect found).
