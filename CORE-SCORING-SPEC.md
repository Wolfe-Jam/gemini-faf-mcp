# FAF Core Scoring Specification: The "Populated, Empty, or Slotignored" Standard

## Overview
This specification defines the universal scoring logic for the **Foundational AI-context Format (FAF)**. It ensures 100% score parity across all FAF implementations (Node, Python, Rust/WASM).

## 1. The Three Technical States
Every FAF slot exists in exactly one of these three states.

| State | Definition | Scoring Impact |
|-------|------------|----------------|
| **Empty** | The default state for all slots. The slot is either missing or contains a generic placeholder. | `Numerator +0`, `Denominator +1` |
| **Populated** | The slot contains valid, project-specific data for the slot type. | `Numerator +1`, `Denominator +1` |
| **Slotignored** | The slot is explicitly marked as not applicable to the project's app-type. | `Numerator +0`, `Denominator +0` |

---

## 2. The Championship Formula
The final FAF score is a percentage calculated strictly against **Active Slots**. All scores are final.

**Formula:**
`Score % = (Total Populated Slots) / (Total Slots - Total Slotignored Slots)`

**Rules:**
- **Initial State:** All 33 slots are **Empty** until populated or slotignored.
- **Minimum Score:** 0%
- **Maximum Score:** 100%

---

## 3. The Universal Slot Map (33 Slots)

### **Base 21 Slots**
| Category | Slots |
| :--- | :--- |
| **Project Meta (3)** | `project.name`, `project.goal`, `project.main_language` |
| **Human Context (6)** | `human.who`, `human.what`, `human.why`, `human.where`, `human.when`, `human.how` |
| **Frontend Stack (4)** | `stack.frontend`, `stack.css_framework`, `stack.ui_library`, `stack.state_management` |
| **Backend Stack (5)** | `stack.backend`, `stack.api_type`, `stack.runtime`, `stack.database`, `stack.connection` |
| **Universal Stack (3)** | `stack.hosting`, `stack.build`, `stack.cicd` |

### **Enterprise +12 Slots**
| Category | Slots |
| :--- | :--- |
| **Infra (5)** | `stack.monorepo_tool`, `stack.package_manager`, `stack.workspaces`, `monorepo.packages_count`, `monorepo.build_orchestrator` |
| **App Layers (4)** | `stack.admin`, `stack.cache`, `stack.search`, `stack.storage` |
| **Operations (3)** | `monorepo.versioning_strategy`, `monorepo.shared_configs`, `monorepo.remote_cache` |

---

## 4. Implementation Rules

### **Rule 1: Placeholder Rejection**
Implementations MUST treat generic placeholders as **Empty**. 
- *Examples:* "Describe your project goal", "Development teams", "Cloud platform".

### **Rule 2: Type-Agnostic Engine**
The scoring engine is agnostic to the project `type`. App-types (e.g., `cli`, `react`) act as **Configuration Templates** that set the state of specific slots to `slotignored`.

### **Rule 3: Score Finality**
Once calculated based on the 33-slot map and the applied template, the score is considered the final AI-Readiness metric.

---

## 5. Compliance
A tool is considered **FAF-Compliant** only if it produces identical scores to the reference **FAF WASM Scorer**.

---
**Standard Steward:** Wolfe James (@wolfe_jam)
**Reference Implementation:** [faf-wasm-sdk](https://github.com/Wolfe-Jam/faf-wasm-sdk)
