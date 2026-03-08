"""
FAF Model Library — 100% Trophy-scored .faf examples by project type.

Each model is a complete, realistic project.faf that fills all 21 scored slots.
Used by faf_model tool to give AI a reference target for any project type.
"""

MODELS = {
    "mcp-server": {
        "description": "MCP server for AI tool integration (stdio or HTTP)",
        "covers": ["MCP servers", "Gemini extensions", "Claude tools", "AI integrations"],
        "faf": """faf_version: '2.5.0'
project:
  name: weather-mcp
  goal: Real-time weather data for AI assistants via MCP tools
  main_language: Python
stack:
  frontend: null
  backend: Python FastMCP
  database: null
  testing: pytest
human_context:
  who: AI tool developers adding weather awareness to assistants
  what: MCP server with 5 tools — current weather, forecast, alerts, history, location search
  why: AI assistants need real-time weather data without API key management
  where: Local MCP server via stdio, optional Cloud Run deployment
  when: Every AI session that needs weather context
  how: Install extension, tools auto-discover, AI calls them as needed
instant_context:
  what_building: MCP server providing weather data to AI assistants via standardized tools
  tech_stack: Python, FastMCP, OpenWeatherMap API, Cloud Run
  key_files:
    - server.py
    - pyproject.toml
    - tests/test_server.py
  commands:
    test: python -m pytest tests/ -v
    run: python server.py
ai_instructions:
  priority: Read project.faf first for full context
  usage: Code-first, minimal explanations
preferences:
  quality_bar: zero_errors
  commit_style: conventional
state:
  phase: production
  version: 1.0.0
  status: active
""",
    },
    "web-app": {
        "description": "Frontend web application (React, Vue, Angular, Svelte)",
        "covers": ["React", "Vue", "Angular", "Svelte", "Next.js", "SvelteKit", "Nuxt"],
        "faf": """faf_version: '2.5.0'
project:
  name: team-dashboard
  goal: Real-time metrics dashboard for engineering team velocity and sprint progress
  main_language: TypeScript
stack:
  frontend: React + Vite
  backend: Express API
  database: PostgreSQL
  testing: Vitest + Playwright
human_context:
  who: Engineering teams tracking sprint velocity and deployment frequency
  what: Interactive dashboard with charts, filters, and team comparison views
  why: Replace spreadsheet-based reporting with real-time automated metrics
  where: Vercel (frontend), Railway (API + database)
  when: Every standup and sprint review — data refreshes every 5 minutes
  how: GitHub and Jira APIs feed data, dashboard renders metrics, alerts on anomalies
instant_context:
  what_building: React dashboard with real-time engineering metrics and team analytics
  tech_stack: TypeScript, React, Vite, Tailwind, Express, PostgreSQL, Prisma
  key_files:
    - src/App.tsx
    - src/components/Dashboard.tsx
    - api/server.ts
    - prisma/schema.prisma
  commands:
    dev: npm run dev
    test: npm test
    build: npm run build
ai_instructions:
  priority: Read project.faf first for full context
  usage: TypeScript strict mode, component-first architecture
preferences:
  quality_bar: strict_typescript
  commit_style: conventional
state:
  phase: production
  version: 2.1.0
  status: active
""",
    },
    "saas": {
        "description": "SaaS product with auth, billing, and multi-tenancy",
        "covers": ["SaaS", "B2B platforms", "subscription products", "multi-tenant apps"],
        "faf": """faf_version: '2.5.0'
project:
  name: projecthub
  goal: Lightweight project management for small creative teams with time tracking and invoicing
  main_language: TypeScript
stack:
  frontend: SvelteKit
  backend: SvelteKit server routes
  database: PostgreSQL + Drizzle ORM
  testing: Playwright + Vitest
human_context:
  who: Small creative agencies (5-20 people) managing client projects
  what: Kanban boards, time tracking, client portals, and invoicing in one tool
  why: Existing tools are too complex or too expensive for small teams
  where: Cloudflare Pages (frontend), Cloudflare Workers (edge functions)
  when: Launched 6 months ago, 200 paying customers, $8k MRR
  how: Freemium model, self-serve onboarding, Stripe billing, white-label option
instant_context:
  what_building: Multi-tenant SaaS with project management, time tracking, and invoicing
  tech_stack: SvelteKit, TypeScript, Tailwind, PostgreSQL, Drizzle, Stripe, Cloudflare
  key_files:
    - src/routes/+layout.svelte
    - src/lib/server/db.ts
    - src/routes/api/billing/+server.ts
    - drizzle/schema.ts
  commands:
    dev: npm run dev
    test: npm test
    deploy: wrangler pages deploy
ai_instructions:
  priority: Read project.faf first for full context
  usage: Edge-first, minimize server round-trips, tenant isolation mandatory
preferences:
  quality_bar: production_grade
  commit_style: conventional
state:
  phase: production
  version: 3.2.0
  status: active
""",
    },
    "cli-tool": {
        "description": "Command-line tool distributed via package manager or binary",
        "covers": ["CLI tools", "developer tools", "npm packages", "Homebrew", "cargo install"],
        "faf": """faf_version: '2.5.0'
project:
  name: migrator
  goal: Zero-downtime database migrations with rollback support and dry-run mode
  main_language: Go
stack:
  frontend: null
  backend: Go
  database: PostgreSQL + MySQL + SQLite
  testing: go test + table-driven tests
human_context:
  who: Platform engineering teams managing database schemas across environments
  what: CLI tool for version-controlled schema migrations with automatic rollback
  why: Existing tools lack multi-region multi-tenant migration support
  where: Distributed via Homebrew and direct binary downloads
  when: Internal use for 2 years, now open-sourcing
  how: Version-controlled SQL files, dry-run validation, automatic rollback on failure
instant_context:
  what_building: Database migration CLI with zero-downtime deployments and rollback
  tech_stack: Go, cobra, PostgreSQL driver, MySQL driver, SQLite
  key_files:
    - cmd/root.go
    - cmd/migrate.go
    - internal/engine/engine.go
    - internal/driver/postgres.go
  commands:
    build: go build -o migrator
    test: go test ./...
    install: go install
ai_instructions:
  priority: Read project.faf first for full context
  usage: Go idioms, error wrapping, table-driven tests
preferences:
  quality_bar: zero_data_loss
  commit_style: conventional
state:
  phase: production
  version: 2.0.0
  status: active
""",
    },
    "api-service": {
        "description": "Backend API service (REST, GraphQL, gRPC)",
        "covers": ["REST APIs", "GraphQL", "gRPC", "microservices", "serverless functions"],
        "faf": """faf_version: '2.5.0'
project:
  name: payments-api
  goal: Handle subscription billing, invoices, and multi-currency payment processing
  main_language: TypeScript
stack:
  frontend: null
  backend: Fastify
  database: PostgreSQL + Redis
  testing: Jest + Supertest
human_context:
  who: Backend team at fintech startup processing $2M+ monthly recurring revenue
  what: Payment service handling subscriptions, invoicing, and webhook processing
  why: Outgrew Stripe-only setup, need custom billing logic and multi-currency
  where: AWS Lambda (us-east-1, eu-west-1) with RDS and ElastiCache
  when: Production since Q2 2024, processing 50k+ transactions per month
  how: Stripe for payment processing, custom logic for invoicing, webhooks for real-time sync
instant_context:
  what_building: Payment processing API with subscriptions, invoicing, and multi-currency support
  tech_stack: TypeScript, Fastify, PostgreSQL, Redis, Stripe SDK, AWS Lambda
  key_files:
    - src/server.ts
    - src/routes/subscriptions.ts
    - src/routes/webhooks.ts
    - src/services/billing.ts
  commands:
    dev: npm run dev
    test: npm test
    deploy: serverless deploy
ai_instructions:
  priority: Read project.faf first for full context
  usage: Type-safe, idempotent endpoints, structured logging, PCI-aware
preferences:
  quality_bar: zero_runtime_errors
  commit_style: conventional
state:
  phase: production
  version: 4.1.0
  status: active
""",
    },
    "mobile-app": {
        "description": "Mobile application (React Native, Flutter, native iOS/Android)",
        "covers": ["React Native", "Flutter", "iOS", "Swift", "Kotlin", "PWA", "Expo"],
        "faf": """faf_version: '2.5.0'
project:
  name: field-tracker
  goal: Offline-first mobile app for field service technicians to log jobs and capture photos
  main_language: TypeScript
stack:
  frontend: React Native + Expo
  backend: Supabase
  database: SQLite (local) + PostgreSQL (cloud)
  testing: Jest + Detox
human_context:
  who: Field service company with 200+ technicians visiting customer sites daily
  what: Mobile app for job logging, photo capture, signature collection, and offline sync
  why: Paper forms lose data, photos get lost, dispatchers lack real-time visibility
  where: App Store + Google Play, Supabase backend, Cloudflare CDN for images
  when: V1 launched 3 months ago, 150 active users, expanding to 500
  how: Offline SQLite syncs to Supabase when connected, push notifications for dispatch
instant_context:
  what_building: Offline-first mobile app for field service job tracking and photo capture
  tech_stack: React Native, Expo, TypeScript, SQLite, Supabase, Cloudflare R2
  key_files:
    - App.tsx
    - src/screens/JobScreen.tsx
    - src/services/sync.ts
    - src/db/schema.ts
  commands:
    dev: npx expo start
    test: npm test
    build-ios: eas build --platform ios
    build-android: eas build --platform android
ai_instructions:
  priority: Read project.faf first for full context
  usage: Offline-first, battery-conscious, handle poor connectivity gracefully
preferences:
  quality_bar: crash_free
  commit_style: conventional
state:
  phase: production
  version: 1.3.0
  status: active
""",
    },
    "chrome-extension": {
        "description": "Browser extension (Chrome, Firefox, Edge)",
        "covers": ["Chrome extensions", "Firefox add-ons", "Edge extensions", "browser plugins", "Manifest V3"],
        "faf": """faf_version: '2.5.0'
project:
  name: tab-saver
  goal: Save and restore browser tab groups with one click, synced across devices
  main_language: TypeScript
stack:
  frontend: Preact + Tailwind
  backend: Chrome Extension Manifest V3
  database: Chrome Storage API + IndexedDB
  testing: Vitest + Puppeteer
human_context:
  who: Knowledge workers with 50+ tabs open who lose context switching between tasks
  what: Extension to save, name, and restore tab groups with keyboard shortcuts
  why: Chrome tab groups disappear on crash, no sync between devices, no search
  where: Chrome Web Store, Edge Add-ons, Firefox Add-ons
  when: 10k+ users, 4.7 star rating, launched 8 months ago
  how: Service worker manages groups, popup for quick access, sync via Chrome Storage
instant_context:
  what_building: Browser extension for saving and restoring tab groups across devices
  tech_stack: TypeScript, Preact, Tailwind, Chrome Extension API, Manifest V3
  key_files:
    - manifest.json
    - src/background.ts
    - src/popup/Popup.tsx
    - src/content/content.ts
  commands:
    dev: npm run dev
    build: npm run build
    test: npm test
ai_instructions:
  priority: Read project.faf first for full context
  usage: Minimal permissions, fast popup render, respect user privacy
preferences:
  quality_bar: zero_errors
  commit_style: conventional
state:
  phase: production
  version: 2.4.0
  status: active
""",
    },
    "python-ml": {
        "description": "Machine learning or data science project",
        "covers": ["ML pipelines", "data science", "PyTorch", "TensorFlow", "LLM apps", "RAG", "computer vision"],
        "faf": """faf_version: '2.5.0'
project:
  name: doc-classifier
  goal: Classify legal documents and extract key clauses using fine-tuned models
  main_language: Python
stack:
  frontend: Streamlit
  backend: FastAPI
  database: Qdrant (vector) + PostgreSQL (metadata)
  testing: pytest + model evaluation suite
human_context:
  who: ML team at legal tech company — 2 ML engineers, 1 backend developer
  what: Document classification (contracts, NDAs, amendments) and clause extraction
  why: Lawyers spend 40% of time on document review — automate the obvious parts
  where: Modal for inference, S3 for storage, on-prem GPU cluster for training
  when: Beta with 5 law firms, targeting GA next quarter
  how: Fine-tuned BERT for classification, GPT-4 for extraction, human review for edge cases
instant_context:
  what_building: Document classification and extraction pipeline for legal documents
  tech_stack: Python, FastAPI, PyTorch, sentence-transformers, Qdrant, Celery, Redis
  key_files:
    - src/classifier/model.py
    - src/extractor/pipeline.py
    - api/main.py
    - notebooks/training.ipynb
  commands:
    train: python -m src.classifier.train
    serve: uvicorn api.main:app
    test: pytest tests/ -v
    evaluate: python -m src.evaluate
ai_instructions:
  priority: Read project.faf first for full context
  usage: Reproducible results, pin all dependencies, document model decisions
preferences:
  quality_bar: reproducible_results
  commit_style: conventional
state:
  phase: beta
  version: 0.9.0
  status: active
""",
    },
    "rust-crate": {
        "description": "Rust library or application published to crates.io",
        "covers": ["Rust crates", "cargo", "systems programming", "WASM", "embedded Rust"],
        "faf": """faf_version: '2.5.0'
project:
  name: fast-compress
  goal: Zero-copy compression library with SIMD acceleration for structured data
  main_language: Rust
stack:
  frontend: null
  backend: Rust
  database: null
  testing: cargo test + criterion benchmarks
human_context:
  who: Systems programmers needing fast compression for network protocols and storage
  what: Compression library supporting LZ4, Zstd, and custom format with zero-copy API
  why: Existing crates copy data unnecessarily — 3x overhead on hot paths
  where: crates.io, supports no_std for embedded use
  when: v1.0 released, 500+ downloads/week, used by 3 production systems
  how: SIMD-accelerated compression, zero-copy decompression, compile-time format selection
instant_context:
  what_building: Zero-copy compression library with SIMD acceleration for Rust
  tech_stack: Rust, SIMD intrinsics, no_std compatible, criterion for benchmarks
  key_files:
    - src/lib.rs
    - src/compress.rs
    - src/decompress.rs
    - benches/throughput.rs
  commands:
    test: cargo test
    bench: cargo bench
    publish: cargo publish
ai_instructions:
  priority: Read project.faf first for full context
  usage: Unsafe only when benchmarked, document safety invariants, no_std by default
preferences:
  quality_bar: zero_undefined_behavior
  commit_style: conventional
state:
  phase: production
  version: 1.2.0
  status: active
""",
    },
    "library": {
        "description": "Reusable library or SDK (npm, PyPI, crates.io, etc.)",
        "covers": ["npm packages", "PyPI packages", "SDKs", "component libraries", "shared utilities"],
        "faf": """faf_version: '2.5.0'
project:
  name: date-engine
  goal: Lightweight date manipulation library with timezone support and human-readable output
  main_language: TypeScript
stack:
  frontend: null
  backend: TypeScript (ESM + CJS)
  database: null
  testing: Vitest + timezone fixtures
human_context:
  who: JavaScript developers tired of moment.js bloat and date-fns complexity
  what: Date library with chainable API, timezone support, and locale-aware formatting
  why: day.js lacks timezone, date-fns is too functional, Temporal is not ready yet
  where: npm registry, works in Node, Bun, Deno, and browsers
  when: Published 1 year ago, 2k+ weekly downloads, 400+ GitHub stars
  how: Tree-shakeable ESM, < 5KB gzipped, drop-in for common date-fns use cases
instant_context:
  what_building: Lightweight date manipulation library with timezone and locale support
  tech_stack: TypeScript, Vitest, tsup bundler, ESM + CJS dual publish
  key_files:
    - src/index.ts
    - src/timezone.ts
    - src/format.ts
    - src/locale/en.ts
  commands:
    dev: npm run dev
    test: npm test
    build: npm run build
    publish: npm publish
ai_instructions:
  priority: Read project.faf first for full context
  usage: Zero dependencies, tree-shakeable exports, 100% test coverage
preferences:
  quality_bar: zero_breaking_changes
  commit_style: conventional
state:
  phase: production
  version: 3.0.0
  status: active
""",
    },
    "monorepo": {
        "description": "Multi-package monorepo (Turborepo, Nx, pnpm workspaces)",
        "covers": ["monorepos", "Turborepo", "Nx", "Lerna", "pnpm workspaces", "multi-app"],
        "faf": """faf_version: '2.5.0'
project:
  name: shopfront
  goal: Headless e-commerce platform with shared component library and admin panel
  main_language: TypeScript
stack:
  frontend: Next.js (storefront) + React (admin)
  backend: Fastify API
  database: PostgreSQL + Redis + Meilisearch
  testing: Vitest + Playwright + Turborepo test pipeline
human_context:
  who: E-commerce agency building custom storefronts for fashion brands
  what: Headless commerce with storefront, admin panel, API, shared UI, and database package
  why: Shopify too limiting, custom builds too expensive to maintain per client
  where: Vercel (apps), Railway (services), Cloudflare R2 (assets)
  when: 3 clients live, 2 in development, targeting 10 by end of year
  how: Shared core packages, client-specific themes, white-label admin, pnpm workspaces
instant_context:
  what_building: Multi-package e-commerce platform with storefront, admin, API, and shared packages
  tech_stack: TypeScript, Turborepo, pnpm, Next.js, React, Fastify, Prisma, PostgreSQL
  key_files:
    - turbo.json
    - apps/web/src/app/page.tsx
    - apps/admin/src/App.tsx
    - packages/ui/src/index.ts
    - packages/db/prisma/schema.prisma
  commands:
    dev: turbo dev
    test: turbo test
    build: turbo build
    lint: turbo lint
ai_instructions:
  priority: Read project.faf first for full context
  usage: Changes to packages/ affect all apps — test everything. Respect workspace boundaries.
preferences:
  quality_bar: production_grade
  commit_style: conventional
state:
  phase: production
  version: 2.0.0
  status: active
""",
    },
    "android-app": {
        "description": "Android native application (Kotlin, Jetpack Compose)",
        "covers": ["Android", "Kotlin", "Jetpack Compose", "Material Design", "Google Play"],
        "faf": """faf_version: '2.5.0'
project:
  name: fit-log
  goal: Workout tracking app with exercise recognition and progress visualization
  main_language: Kotlin
stack:
  frontend: Jetpack Compose + Material 3
  backend: Firebase
  database: Room (local) + Firestore (cloud)
  testing: JUnit + Espresso + Compose Test
human_context:
  who: Fitness enthusiasts who want simple workout logging without social media noise
  what: Track exercises, sets, reps, and weight with auto-suggestions and progress charts
  why: Most fitness apps are bloated with social features — users just want to log and track
  where: Google Play Store, Firebase backend, ML Kit for exercise recognition
  when: 50k+ installs, 4.5 star rating, launched 1 year ago
  how: Room DB for offline logging, Firestore sync, ML Kit pose detection for form feedback
instant_context:
  what_building: Android workout tracker with exercise recognition and progress charts
  tech_stack: Kotlin, Jetpack Compose, Room, Firebase, ML Kit, Hilt, Coroutines
  key_files:
    - app/src/main/java/com/fitlog/MainActivity.kt
    - app/src/main/java/com/fitlog/ui/WorkoutScreen.kt
    - app/src/main/java/com/fitlog/data/WorkoutDao.kt
    - app/build.gradle.kts
  commands:
    build: ./gradlew assembleDebug
    test: ./gradlew test
    lint: ./gradlew lint
ai_instructions:
  priority: Read project.faf first for full context
  usage: Compose-first UI, coroutines for async, Hilt for DI, follow Material 3 guidelines
preferences:
  quality_bar: crash_free
  commit_style: conventional
state:
  phase: production
  version: 2.3.0
  status: active
""",
    },
    "iot-device": {
        "description": "IoT, embedded, or hardware project (Arduino, Raspberry Pi, ESP32)",
        "covers": ["IoT", "embedded systems", "Arduino", "Raspberry Pi", "ESP32", "Matter", "smart home"],
        "faf": """faf_version: '2.5.0'
project:
  name: greenhouse-monitor
  goal: Automated greenhouse monitoring with soil moisture, temperature, and light sensors
  main_language: C++
stack:
  frontend: Vue.js dashboard
  backend: ESP32 + MQTT broker
  database: InfluxDB (time series)
  testing: PlatformIO unit tests + integration tests
human_context:
  who: Urban farmers and hobbyist gardeners automating greenhouse conditions
  what: Sensor network that monitors soil, air, light and auto-controls watering and ventilation
  why: Manual monitoring wastes time and plants die when you forget to water
  where: ESP32 devices in greenhouse, Raspberry Pi hub, cloud dashboard
  when: 20 beta testers, open-source hardware design, kit sales starting next month
  how: ESP32 reads sensors via I2C/analog, publishes MQTT, Pi aggregates, Vue dashboard displays
instant_context:
  what_building: IoT sensor network for automated greenhouse monitoring and control
  tech_stack: C++, PlatformIO, ESP32, MQTT, InfluxDB, Vue.js, Raspberry Pi
  key_files:
    - src/main.cpp
    - src/sensors/moisture.h
    - src/actuators/pump.h
    - dashboard/src/App.vue
  commands:
    build: pio run
    upload: pio run --target upload
    monitor: pio device monitor
    test: pio test
ai_instructions:
  priority: Read project.faf first for full context
  usage: Memory-constrained, avoid dynamic allocation, handle sensor failures gracefully
preferences:
  quality_bar: hardware_reliable
  commit_style: conventional
state:
  phase: beta
  version: 0.8.0
  status: active
""",
    },
    "desktop-app": {
        "description": "Desktop application (Electron, Tauri, native)",
        "covers": ["Electron", "Tauri", "WPF", "Qt", "cross-platform desktop", "macOS", "Windows", "Linux"],
        "faf": """faf_version: '2.5.0'
project:
  name: markdown-studio
  goal: Distraction-free Markdown editor with live preview, vim keybindings, and local file management
  main_language: TypeScript
stack:
  frontend: Solid.js + CodeMirror
  backend: Tauri (Rust)
  database: SQLite (file index)
  testing: Vitest + Tauri integration tests
human_context:
  who: Developers and writers who want a fast, private, local-first Markdown editor
  what: Desktop editor with split pane preview, vim mode, file tree, and full-text search
  why: VS Code is too heavy, web editors require internet, Obsidian has too many features
  where: macOS, Windows, Linux — distributed via GitHub Releases and Homebrew
  when: 5k downloads, growing 20% month over month, launched 4 months ago
  how: Tauri for native shell, CodeMirror for editing, remark for rendering, SQLite for search index
instant_context:
  what_building: Cross-platform Markdown editor with live preview and vim keybindings
  tech_stack: TypeScript, Solid.js, Tauri, Rust, CodeMirror, SQLite, remark
  key_files:
    - src/App.tsx
    - src/editor/Editor.tsx
    - src-tauri/src/main.rs
    - src-tauri/src/file_manager.rs
  commands:
    dev: cargo tauri dev
    build: cargo tauri build
    test: npm test
ai_instructions:
  priority: Read project.faf first for full context
  usage: Native performance, minimal memory footprint, respect OS conventions per platform
preferences:
  quality_bar: native_quality
  commit_style: conventional
state:
  phase: production
  version: 1.5.0
  status: active
""",
    },
    "game": {
        "description": "Game or interactive experience (Unity, Godot, web, native)",
        "covers": ["Unity", "Godot", "Unreal", "Phaser", "WebGL", "game development", "interactive"],
        "faf": """faf_version: '2.5.0'
project:
  name: pixel-quest
  goal: Procedurally generated roguelike with pixel art and permadeath
  main_language: GDScript
stack:
  frontend: Godot Engine 4.2
  backend: null
  database: Local save files (JSON)
  testing: GdUnit4 + playtesting scripts
human_context:
  who: Indie game studio (2 developers, 1 artist) making retro-style games
  what: Top-down roguelike with procedural dungeons, 50+ items, and boss fights
  why: Love classic roguelikes but want modern quality-of-life and accessibility features
  where: Steam, itch.io, planned Switch port
  when: Early access launched 2 months ago, 3k wishlists, targeting v1.0 in 6 months
  how: Godot for engine, Wave Function Collapse for dungeon gen, Aseprite for sprites
instant_context:
  what_building: Procedural roguelike game with pixel art, permadeath, and 50+ items
  tech_stack: Godot 4.2, GDScript, Wave Function Collapse, Aseprite, Steam SDK
  key_files:
    - scenes/main.tscn
    - scripts/player/player.gd
    - scripts/generation/dungeon_generator.gd
    - scripts/items/item_database.gd
  commands:
    run: godot --path . scenes/main.tscn
    test: godot --headless --script tests/run_tests.gd
    export: godot --headless --export-release "Linux"
ai_instructions:
  priority: Read project.faf first for full context
  usage: Performance matters — 60fps minimum, pool objects, avoid allocations in game loop
preferences:
  quality_bar: fun_first
  commit_style: conventional
state:
  phase: early_access
  version: 0.6.0
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
