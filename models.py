"""
FAF Model Library — 100% Trophy-scored .faf examples by project type.

Each model is a complete, realistic project.faf that fills all 21 scored slots.
Used by the faf_model tool to give AI a reference target for any project type.
"""

MODELS = {
    "mcp-server": {
        "description": "MCP server for AI tool integration (stdio or HTTP)",
        "covers": ["MCP servers", "Gemini extensions", "Claude tools", "AI integrations"],
        "faf": """faf_version: "3.0"
project:
  name: "weather-mcp"
  goal: "Real-time weather data for AI assistants via MCP tools"
  main_language: "Python"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: "FastMCP"
  api_type: "MCP (stdio) + HTTP/REST"
  runtime: "Python 3.11+"
  database: slotignored
  connection: "stdio + Streamable HTTP"
  hosting: "Google Cloud Run"
  build: "hatchling"
  cicd: "GitHub Actions"
  package_manager: "pip"
human_context:
  who: "AI tool developers adding weather awareness to assistants"
  what: "MCP server with 5 tools — current weather, forecast, alerts, history, location search"
  why: "AI assistants need real-time weather data without per-project API key wiring"
  where: "Local MCP server via stdio; optional Streamable HTTP on Cloud Run"
  when: "Every AI session that needs weather context"
  how: "Install the extension, tools auto-discover, the assistant calls them as needed"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "web-app": {
        "description": "Frontend web application (React, Vue, Angular, Svelte)",
        "covers": ["React", "Vue", "Angular", "Svelte", "Next.js", "SvelteKit", "Nuxt"],
        "faf": """faf_version: "3.0"
project:
  name: "sprint-dashboard"
  goal: "Real-time engineering metrics dashboard replacing spreadsheet reporting"
  main_language: "TypeScript"
stack:
  frontend: "React + Vite"
  css_framework: "Tailwind CSS"
  ui_library: "shadcn/ui"
  state_management: "Zustand"
  backend: "Express"
  api_type: "REST"
  runtime: "Node.js 20"
  database: "PostgreSQL"
  connection: "Prisma"
  hosting: "Vercel (web) + Railway (API)"
  build: "Vite"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
human_context:
  who: "Engineering teams tracking sprint velocity and deployment frequency"
  what: "Interactive dashboard with charts, filters, and team comparison views"
  why: "Replace spreadsheet-based reporting with real-time automated metrics"
  where: "Vercel for the frontend, Railway for the API and Postgres"
  when: "Production — checked daily in standup"
  how: "React SPA calls a REST API that aggregates CI and issue-tracker data"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "saas": {
        "description": "SaaS product with auth, billing, and multi-tenancy",
        "covers": ["SaaS", "B2B platforms", "subscription products", "multi-tenant apps"],
        "faf": """faf_version: "3.0"
project:
  name: "feedbackloop"
  goal: "Multi-tenant customer-feedback platform with per-workspace billing"
  main_language: "TypeScript"
stack:
  frontend: "Next.js (App Router)"
  css_framework: "Tailwind CSS"
  ui_library: "Radix UI"
  state_management: "TanStack Query"
  backend: "Next.js API routes"
  api_type: "REST + tRPC"
  runtime: "Node.js 20"
  database: "PostgreSQL (row-level tenancy)"
  connection: "Drizzle ORM"
  hosting: "Vercel"
  build: "Turbopack"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
human_context:
  who: "Product teams collecting and triaging customer feedback across workspaces"
  what: "Feedback boards, roadmaps, and changelogs with Stripe-metered seats"
  why: "Teams outgrow shared inboxes and spreadsheets for feature requests"
  where: "Vercel edge + a managed Postgres (Neon)"
  when: "Production — paid plans live"
  how: "Next.js App Router, tRPC for the typed API, Stripe webhooks for billing state"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "cli-tool": {
        "description": "Command-line tool distributed via package manager or binary",
        "covers": ["CLI tools", "developer tools", "npm packages", "Homebrew", "cargo install"],
        "faf": """faf_version: "3.0"
project:
  name: "portscan"
  goal: "Fast concurrent TCP port scanner with JSON output for CI pipelines"
  main_language: "Go"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Go 1.22"
  database: slotignored
  connection: slotignored
  hosting: "Homebrew + GitHub Releases"
  build: "go build"
  cicd: "GitHub Actions"
  package_manager: "go modules"
human_context:
  who: "Platform engineers scripting network checks in build pipelines"
  what: "Single static binary that scans a host or CIDR and emits JSON or a table"
  why: "nmap is heavy and its output is hard to parse in scripts"
  where: "Developer laptops and CI runners — a single cross-compiled binary"
  when: "Stable — 1.x, semver"
  how: "Goroutine worker pool over a channel of targets, context-cancelled on timeout"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "api-service": {
        "description": "Backend API service (REST, GraphQL, gRPC)",
        "covers": ["REST APIs", "GraphQL", "gRPC", "microservices", "serverless functions"],
        "faf": """faf_version: "3.0"
project:
  name: "orders-api"
  goal: "Order-management REST API for an e-commerce backend"
  main_language: "Python"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: "FastAPI"
  api_type: "REST + OpenAPI"
  runtime: "Python 3.12"
  database: "PostgreSQL"
  connection: "SQLAlchemy + asyncpg"
  hosting: "AWS ECS Fargate"
  build: "Docker"
  cicd: "GitHub Actions"
  package_manager: "uv"
human_context:
  who: "Frontend and mobile teams consuming the order lifecycle"
  what: "CRUD plus state transitions (placed, paid, shipped, refunded) with webhooks"
  why: "The monolith's order logic needed to be a separately scalable service"
  where: "AWS ECS Fargate behind an ALB, RDS Postgres"
  when: "Production — handles live checkout traffic"
  how: "FastAPI with async SQLAlchemy, Alembic migrations, Pydantic schemas"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "mobile-app": {
        "description": "Mobile application (React Native, Flutter, native iOS/Android)",
        "covers": ["React Native", "Flutter", "iOS", "Swift", "Kotlin", "PWA", "Expo"],
        "faf": """faf_version: "3.0"
project:
  name: "trailmate"
  goal: "Offline-first hiking companion with GPS tracks and trail notes"
  main_language: "TypeScript"
stack:
  frontend: "React Native (Expo)"
  css_framework: "NativeWind"
  ui_library: "Tamagui"
  state_management: "Redux Toolkit"
  backend: "Supabase"
  api_type: "REST"
  runtime: "Hermes (RN 0.74)"
  database: "PostgreSQL (Supabase) + SQLite cache"
  connection: "supabase-js"
  hosting: "App Store + Google Play (EAS)"
  build: "EAS Build"
  cicd: "GitHub Actions + EAS"
  package_manager: "npm"
human_context:
  who: "Day hikers and backpackers who lose signal on the trail"
  what: "Record GPS tracks, drop waypoints, and sync notes when back online"
  why: "Most trail apps assume connectivity and fail exactly where you need them"
  where: "App Store and Google Play, built and submitted through EAS"
  when: "Beta — TestFlight and Play internal testing"
  how: "Expo + React Native, local SQLite as the source of truth, Supabase sync on reconnect"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "chrome-extension": {
        "description": "Browser extension (Chrome, Firefox, Edge)",
        "covers": ["Chrome extensions", "Firefox add-ons", "Edge extensions", "browser plugins", "Manifest V3"],
        "faf": """faf_version: "3.0"
project:
  name: "tabtidy"
  goal: "Group and suspend idle browser tabs to reclaim memory"
  main_language: "TypeScript"
stack:
  frontend: "React"
  css_framework: "CSS Modules"
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Chrome MV3 service worker"
  database: slotignored
  connection: "chrome.storage.local"
  hosting: "Chrome Web Store"
  build: "Vite + CRXJS"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
human_context:
  who: "Tab hoarders whose browser eats RAM by mid-afternoon"
  what: "Auto-groups tabs by domain and suspends ones untouched for N minutes"
  why: "Native tab groups do not suspend, and manual cleanup never happens"
  where: "Chrome Web Store — a Manifest V3 extension"
  when: "Published — 1.x on the Web Store"
  how: "MV3 service worker on the tabs and alarms APIs, React popup for settings"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "python-ml": {
        "description": "Machine learning or data science project",
        "covers": ["ML pipelines", "data science", "PyTorch", "TensorFlow", "LLM apps", "RAG", "computer vision"],
        "faf": """faf_version: "3.0"
project:
  name: "churn-model"
  goal: "Weekly customer-churn prediction pipeline feeding the CRM"
  main_language: "Python"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Python 3.11 + CUDA 12"
  database: slotignored
  connection: slotignored
  hosting: "Vertex AI Pipelines"
  build: "uv"
  cicd: "GitHub Actions"
  package_manager: "uv"
human_context:
  who: "The growth team acting on at-risk accounts"
  what: "Feature build, XGBoost training, evaluation, and a scored CSV to the CRM"
  why: "Manual churn heuristics missed the accounts that actually left"
  where: "Vertex AI Pipelines on a schedule; experiments tracked in Weights & Biases"
  when: "Production — retrains weekly"
  how: "A DVC-tracked pipeline: extract → features → train → evaluate → publish"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "rust-crate": {
        "description": "Rust library or application published to crates.io",
        "covers": ["Rust crates", "cargo", "systems programming", "WASM", "embedded Rust"],
        "faf": """faf_version: "3.0"
project:
  name: "ratelim"
  goal: "Lock-free token-bucket rate limiter for async Rust services"
  main_language: "Rust"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Rust 1.79 (edition 2021)"
  database: slotignored
  connection: slotignored
  hosting: "crates.io"
  build: "cargo"
  cicd: "GitHub Actions"
  package_manager: "cargo"
human_context:
  who: "Rust service authors who need backpressure without a Redis round-trip"
  what: "A `Governor`-style limiter with per-key buckets and a Tokio-friendly API"
  why: "Most limiters lock a mutex per request; this one uses atomics"
  where: "crates.io — a library crate, `no_std` optional"
  when: "Stable — 1.x, MSRV pinned"
  how: "Atomic compare-and-swap on a packed (tokens, timestamp) u64 per key"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "library": {
        "description": "Reusable library or SDK (npm, PyPI, crates.io, etc.)",
        "covers": ["npm packages", "PyPI packages", "SDKs", "component libraries", "shared utilities"],
        "faf": """faf_version: "3.0"
project:
  name: "tinyvalidate"
  goal: "1 kB schema validator with static type inference for form inputs"
  main_language: "TypeScript"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Node.js 18+ and browsers (ESM + CJS)"
  database: slotignored
  connection: slotignored
  hosting: "npm"
  build: "tsup"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
human_context:
  who: "Frontend developers who find Zod too big for a landing page"
  what: "A composable validator that infers a TypeScript type from the schema"
  why: "Bundle budgets matter and most validators ship 12 kB+"
  where: "npm — dual ESM/CJS, zero dependencies"
  when: "Stable — 1.x, semver, tree-shakeable"
  how: "Chainable rule objects; a single `parse` walks them and narrows the type"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "monorepo": {
        "description": "Multi-package monorepo (Turborepo, Nx, pnpm workspaces)",
        "covers": ["monorepos", "Turborepo", "Nx", "Lerna", "pnpm workspaces", "multi-app"],
        "faf": """faf_version: "3.0"
project:
  name: "acme-platform"
  goal: "Turborepo housing the marketing site, the app, and the shared design system"
  main_language: "TypeScript"
stack:
  frontend: "Next.js (apps/web)"
  css_framework: "Tailwind CSS"
  ui_library: "@acme/ui (shared)"
  state_management: "TanStack Query"
  backend: "NestJS (apps/api)"
  api_type: "REST + GraphQL"
  runtime: "Node.js 20"
  database: "PostgreSQL"
  connection: "Prisma"
  hosting: "Vercel (web) + Fly.io (api)"
  build: "Turborepo"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
  monorepo_tool: "Turborepo"
  workspaces: "pnpm workspaces"
human_context:
  who: "A product team sharing UI and types across a site, an app, and an API"
  what: "Two Next.js apps, a NestJS API, and shared `ui` / `config` / `tsconfig` packages"
  why: "Copy-pasting components and types between three repos kept drifting"
  where: "Vercel for the web apps, Fly.io for the API, one Postgres"
  when: "Production — all three apps deploy from this repo"
  how: "pnpm workspaces + Turborepo task graph with remote caching"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "android-app": {
        "description": "Android native application (Kotlin, Jetpack Compose)",
        "covers": ["Android", "Kotlin", "Jetpack Compose", "Material Design", "Google Play"],
        "faf": """faf_version: "3.0"
project:
  name: "pocketledger"
  goal: "Envelope-budgeting app that works fully offline"
  main_language: "Kotlin"
stack:
  frontend: "Jetpack Compose"
  css_framework: slotignored
  ui_library: "Material 3"
  state_management: "ViewModel + StateFlow"
  backend: slotignored
  api_type: "REST"
  runtime: "Android 8+ (API 26)"
  database: "Room (SQLite)"
  connection: "Retrofit"
  hosting: "Google Play"
  build: "Gradle (Kotlin DSL)"
  cicd: "GitHub Actions"
  package_manager: "gradle"
human_context:
  who: "People who budget by envelope and do not want their bank data in the cloud"
  what: "Accounts, envelopes, and transactions with an optional encrypted backup"
  why: "Most budget apps require linking a bank and a subscription"
  where: "Google Play — phone and tablet, offline-first"
  when: "Published — 2.x on Play"
  how: "Single-activity Compose, Room as the store, WorkManager for the backup job"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "iot-device": {
        "description": "IoT, embedded, or hardware project (Arduino, Raspberry Pi, ESP32)",
        "covers": ["IoT", "embedded systems", "Arduino", "Raspberry Pi", "ESP32", "Matter", "smart home"],
        "faf": """faf_version: "3.0"
project:
  name: "soil-sensor"
  goal: "Battery ESP32 soil-moisture sensor reporting over MQTT"
  main_language: "Rust"
stack:
  frontend: slotignored
  css_framework: slotignored
  ui_library: slotignored
  state_management: slotignored
  backend: slotignored
  api_type: "MQTT"
  runtime: "ESP32-C3 (no_std, Embassy)"
  database: slotignored
  connection: "MQTT over TLS"
  hosting: "AWS IoT Core (OTA)"
  build: "cargo + espflash"
  cicd: "GitHub Actions"
  package_manager: "cargo"
human_context:
  who: "Home gardeners and a small greenhouse operation"
  what: "Reads capacitive moisture and temperature every 15 min, deep-sleeps between"
  why: "Off-the-shelf sensors are cloud-locked and drain a coin cell in a week"
  where: "Field devices reporting to AWS IoT Core; firmware updated OTA"
  when: "Fleet pilot — a dozen units deployed"
  how: "Embassy async on a single core, TLS-MQTT publish, then `deep_sleep`"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "desktop-app": {
        "description": "Desktop application (Electron, Tauri, native)",
        "covers": ["Electron", "Tauri", "WPF", "Qt", "cross-platform desktop", "macOS", "Windows", "Linux"],
        "faf": """faf_version: "3.0"
project:
  name: "markvault"
  goal: "Local-first Markdown notes app with full-text search"
  main_language: "TypeScript"
stack:
  frontend: "React"
  css_framework: "Tailwind CSS"
  ui_library: "shadcn/ui"
  state_management: "Zustand"
  backend: "Rust (Tauri core)"
  api_type: slotignored
  runtime: "Tauri 2 (WebView2 / WebKitGTK)"
  database: "SQLite (tauri-plugin-sql)"
  connection: "Tauri IPC"
  hosting: "GitHub Releases (auto-update)"
  build: "Tauri CLI + Vite"
  cicd: "GitHub Actions"
  package_manager: "pnpm"
human_context:
  who: "Writers and developers who want their notes as plain files on disk"
  what: "A folder of Markdown files with an FTS5 index, tags, and backlinks"
  why: "Cloud note apps own your data and go down; the files should be yours"
  where: "GitHub Releases — signed macOS, Windows, and Linux builds with auto-update"
  when: "1.x — stable, notarized"
  how: "React UI in a Tauri window, Rust owns the filesystem and the SQLite index"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "game": {
        "description": "Game or interactive experience (Unity, Godot, web, native)",
        "covers": ["Unity", "Godot", "Unreal", "Phaser", "WebGL", "game development", "interactive"],
        "faf": """faf_version: "3.0"
project:
  name: "depths"
  goal: "Roguelike diver — procedural caves, oxygen management, permadeath"
  main_language: "GDScript"
stack:
  frontend: "Godot 4 (GDScript)"
  css_framework: slotignored
  ui_library: "Godot Control nodes"
  state_management: slotignored
  backend: slotignored
  api_type: slotignored
  runtime: "Godot 4.2"
  database: slotignored
  connection: slotignored
  hosting: "Steam + itch.io"
  build: "Godot export templates"
  cicd: "GitHub Actions"
  package_manager: slotignored
human_context:
  who: "Players who like tense, short roguelike runs"
  what: "Descend procedurally generated caves, manage oxygen and light, die and restart"
  why: "A focused single-mechanic roguelike, not another sprawling survival craft"
  where: "Steam and itch.io — Windows, macOS, Linux exports"
  when: "Early Access — content updates monthly"
  how: "Godot 4 scenes, a seeded cave generator, resource meters drive the loop"
preferences:
  quality_bar: zero_errors
  commit_style: conventional
  testing: required
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
}

def get_model(project_type: str) -> dict | None:
    """Get a model by project type key."""
    return MODELS.get(project_type)


def list_models() -> list[dict]:
    """List all available models with type, description, and what they cover."""
    return [
        {
            "type": key,
            "description": model["description"],
            "covers": model["covers"],
        }
        for key, model in MODELS.items()
    ]
