# Architectural Exploration and Code Walkthrough Guide

Use this guide for "how does X work" questions, pre-refactoring code walkthroughs, and component/logic placement decisions.

---

## When to Use

Apply this guide when:
- Investigating how a subsystem, data pipeline, or user flow operates end-to-end before touching code.
- Resolving placement and layering questions ("Where should this code live?", "Is this the right layer?", "Should this be a DAL service, custom hook, or Server Component?").
- Onboarding onto an unfamiliar Next.js or React codebase to build an accurate mental model.

---

## Step 1: Assess Complexity

- **Simple scope:** A single component, a hook, or a narrow utility function. One pass is enough: locate the file, read implementation, and trace direct callers.
- **Complex scope:** A full route spanning Server Components, Client components, Server Actions, database queries, and third-party integrations. Decompose into distinct slices before refactoring.

---

## Step 2: Trace the Execution and Data Flow

Follow this 5-step exploration checklist:

1. **Locate the entry point:**
   - Where does this flow start? A route page (`app/**/page.tsx`), an API route handler (`route.ts`), or a client user action (`onClick`, form submit)?
2. **Trace the call chain:**
   - Follow data transformation from origin to rendering.
   - For server paths: Page -> Service / DAL function -> ORM / Database -> Serialization boundary.
   - For client paths: User interaction -> Custom hook state update -> Server Action or SWR trigger -> UI re-render.
3. **Map the key abstractions:**
   - Identify core types, schemas, and service interfaces.
   - Check if states use Discriminated Unions or unvalidated bags.
4. **Identify architectural boundaries:**
   - Pinpoint the exact server-to-client boundary (`'use client'`).
   - Check what serialized data crosses this boundary.
5. **Spot hidden gotchas:**
   - Look for sequential `await` waterfalls, unintended module-level state, hydration mismatches, or missing error boundaries.

---

## Step 3: Layering and Placement Decision Tree

Use this checklist to decide where code belongs:

```text
Is this logic querying a database, reading private env vars, or using an ORM?
  ├── YES ──> Place in `lib/services/` or `lib/dal/` (Data Access Layer)
  └── NO
       │
       Is this stateful client logic (browser events, filters, UI toggles)?
         ├── YES ──> Place in `hooks/` (Custom Hook)
         └── NO
              │
              Is this pure data transformation, formatting, or math?
                ├── YES ──> Place in `lib/utils/` (Pure utility module)
                └── NO
                     │
                     Is this interactive UI markup (buttons, inputs, modals)?
                       ├── YES ──> Place in `components/` as a leaf Client Component
                       └── NO  ──> Place in `components/` or `app/` as a Server Component
```

---

## Step 4: Output Structure for Code Walkthroughs

When presenting an architectural explanation, follow this structure:

1. **Overview:** 1-2 paragraphs defining what the subsystem does and its purpose.
2. **Key Concepts:** Core types, services, and schemas needed to understand the feature.
3. **How It Works:** Step-by-step flow walkthrough. Include a Mermaid sequence or flowchart diagram for multi-stage flows.
4. **Where Things Live:** File and directory map showing the exact paths of relevant files.
5. **Gotchas:** Non-obvious performance pitfalls, serialization limits, or historical quirks.
