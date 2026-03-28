# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Structure

```text
artifacts-monorepo/
├── artifacts/              # Deployable applications
│   └── api-server/         # Express API server
├── lib/                    # Shared libraries
│   ├── api-spec/           # OpenAPI spec + Orval codegen config
│   ├── api-client-react/   # Generated React Query hooks
│   ├── api-zod/            # Generated Zod schemas from OpenAPI
│   └── db/                 # Drizzle ORM schema + DB connection
├── scripts/                # Utility scripts (single workspace package)
│   └── src/                # Individual .ts scripts, run via `pnpm --filter @workspace/scripts run <script>`
├── pnpm-workspace.yaml     # pnpm workspace (artifacts/*, lib/*, lib/integrations/*, scripts)
├── tsconfig.base.json      # Shared TS options (composite, bundler resolution, es2022)
├── tsconfig.json           # Root TS project references
└── package.json            # Root package with hoisted devDeps
```

## TypeScript & Composite Projects

Every package extends `tsconfig.base.json` which sets `composite: true`. The root `tsconfig.json` lists all packages as project references. This means:

- **Always typecheck from the root** — run `pnpm run typecheck` (which runs `tsc --build --emitDeclarationOnly`). This builds the full dependency graph so that cross-package imports resolve correctly. Running `tsc` inside a single package will fail if its dependencies haven't been built yet.
- **`emitDeclarationOnly`** — we only emit `.d.ts` files during typecheck; actual JS bundling is handled by esbuild/tsx/vite...etc, not `tsc`.
- **Project references** — when package A depends on package B, A's `tsconfig.json` must list B in its `references` array. `tsc --build` uses this to determine build order and skip up-to-date packages.

## Root Scripts

- `pnpm run build` — runs `typecheck` first, then recursively runs `build` in all packages that define it
- `pnpm run typecheck` — runs `tsc --build --emitDeclarationOnly` using project references

## Packages

### `artifacts/api-server` (`@workspace/api-server`)

Express 5 API server. Routes live in `src/routes/` and use `@workspace/api-zod` for request and response validation and `@workspace/db` for persistence.

- Entry: `src/index.ts` — reads `PORT`, starts Express
- App setup: `src/app.ts` — mounts CORS, JSON/urlencoded parsing, routes at `/api`
- Routes: `src/routes/index.ts` mounts sub-routers; `src/routes/health.ts` exposes `GET /health` (full path: `/api/health`)
- Depends on: `@workspace/db`, `@workspace/api-zod`
- `pnpm --filter @workspace/api-server run dev` — run the dev server
- `pnpm --filter @workspace/api-server run build` — production esbuild bundle (`dist/index.cjs`)
- Build bundles an allowlist of deps (express, cors, pg, drizzle-orm, zod, etc.) and externalizes the rest

### `lib/db` (`@workspace/db`)

Database layer using Drizzle ORM with PostgreSQL. Exports a Drizzle client instance and schema models.

- `src/index.ts` — creates a `Pool` + Drizzle instance, exports schema
- `src/schema/index.ts` — barrel re-export of all models
- `src/schema/<modelname>.ts` — table definitions with `drizzle-zod` insert schemas (no models definitions exist right now)
- `drizzle.config.ts` — Drizzle Kit config (requires `DATABASE_URL`, automatically provided by Replit)
- Exports: `.` (pool, db, schema), `./schema` (schema only)

Production migrations are handled by Replit when publishing. In development, we just use `pnpm --filter @workspace/db run push`, and we fallback to `pnpm --filter @workspace/db run push-force`.

### `lib/api-spec` (`@workspace/api-spec`)

Owns the OpenAPI 3.1 spec (`openapi.yaml`) and the Orval config (`orval.config.ts`). Running codegen produces output into two sibling packages:

1. `lib/api-client-react/src/generated/` — React Query hooks + fetch client
2. `lib/api-zod/src/generated/` — Zod schemas

Run codegen: `pnpm --filter @workspace/api-spec run codegen`

### `lib/api-zod` (`@workspace/api-zod`)

Generated Zod schemas from the OpenAPI spec (e.g. `HealthCheckResponse`). Used by `api-server` for response validation.

### `lib/api-client-react` (`@workspace/api-client-react`)

Generated React Query hooks and fetch client from the OpenAPI spec (e.g. `useHealthCheck`, `healthCheck`).

### `scripts` (`@workspace/scripts`)

Utility scripts package. Each script is a `.ts` file in `src/` with a corresponding npm script in `package.json`. Run scripts via `pnpm --filter @workspace/scripts run <script>`. Scripts can import any workspace package (e.g., `@workspace/db`) by adding it as a dependency in `scripts/package.json`.

---

## LearNexo Content Engine (Python)

**Location:** `learnexo_content_engine/`

A standalone Python (FastAPI) AI microservice for generating personalized learning content for Nigerian secondary school students. Built for the LearNEXO platform.

### Purpose
Takes a student's already-determined learning style and generates:
- **Stage 2:** A full Nigerian-curriculum-aligned learning path (topics, durations, content formats, WAEC/NECO/JAMB exam tips)
- **Stage 3:** Tailored lesson content for each topic, with format matching the student's learning style

### Stack
- **Language:** Python 3.11
- **Framework:** FastAPI + Uvicorn
- **AI:** LangChain + Groq (llama-3.3-70b-versatile)
- **Validation:** Pydantic v2
- **Port:** 8000

### Files
```
learnexo_content_engine/
├── api.py                    # FastAPI app — 3 REST endpoints
├── models.py                 # Pydantic input/output schemas
├── prompts.py                # LangChain prompt templates (one per learning style)
├── llm_config.py             # Groq LLM configuration
├── learning_path_generator.py # Stage 2: learning path generation
├── content_generator.py      # Stage 3: content generation per style
├── example_usage.py          # Interactive demo (run directly)
├── requirements.txt          # Python dependencies
├── .env                      # GROQ_API_KEY (not committed)
└── .env.example              # Template for backend engineers
```

### API Endpoints
- `GET  /health`        → Service health check
- `POST /learning-path` → Stage 2: generate a learning path
- `POST /content`       → Stage 3: generate lesson content for a topic
- `POST /full-pipeline` → Stages 2+3 combined (learning path + first topic content)

### Learning Styles Supported
| Style | Content Format |
|---|---|
| **Visual** | Concept maps, diagram descriptions, infographics, colour-coded notes, Nigerian visual examples |
| **Auditory** | Full narration scripts, mnemonics, storytelling narratives, discussion questions, podcast-style Q&A |
| **Kinesthetic** | Hands-on activities, experiments with everyday items, group tasks, real-world Nigerian applications |

### Run locally
```bash
cd learnexo_content_engine
pip install -r requirements.txt
# Add GROQ_API_KEY to .env
uvicorn api:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### Environment Variables
- `GROQ_API_KEY` — required. Get from https://console.groq.com
