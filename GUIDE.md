# 📖 Nexia Complete Guide

**Everything you need to know about Nexia.**

---

## Table of Contents

1. [What is Nexia?](#what-is-nexia)
2. [Installation](#installation)
3. [Quick Setup](#quick-setup)
4. [How It Works](#how-it-works)
5. [All Commands](#all-commands)
6. [Workflows](#workflows)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## What is Nexia?

Nexia is a **smart documentation system** for AI agents that:

- **Indexes docs once** - Build smart index, reuse forever
- **Queries smartly** - Get only relevant sections (95% reduction)
- **Remembers builds** - Track what you've built
- **Auto-instructs agents** - Read `.nexia-config`, auto-know what to do

**Result:** 75% token savings, massive code reuse, zero friction.

---

## Installation

### Prerequisites

- Python 3.9+
- Your documentation in `./docs` folder

### Step 1: Clone Repository

```bash
git clone https://github.com/aatizaz/nexia.git
cd nexia
```

### Step 2: Add Nexia to Your Project

Copy 3 files to your project root:
1. `nexia-index.py`
2. `nexia-memory.py`
3. `.nexia-config`

### Step 3: Copy Your Docs

```bash
cp -r /path/to/your/docs ./docs
```

Your folder structure:
```
my-project/
├── docs/                    # Your documentation
├── nexia-index.py
├── nexia-memory.py
├── .nexia-config
└── src/                     # Your code
```

---

## Quick Setup

### One-Time Index Build

```bash
python nexia-index.py --build --input ./docs
```

This creates `.nexia/index.json` (persistent, never rebuild).

**Output:**
```
✅ Index built!
   Documents: 10
   Sections: 47
   Code blocks: 12
   Tables: 8
   Keywords indexed: 156

💾 Index saved to .nexia/index.json
```

### That's It!

Agent automatically knows what to do from `.nexia-config`.

---

## How It Works

### Session 1: First Build

```
User: "Build authentication endpoint"
  ↓
Agent reads: .nexia-config
  ↓
Agent runs: python nexia-index.py --build --input ./docs
  ↓
Agent queries: python nexia-index.py --query authentication
  ↓
Agent gets: Only auth-related sections (9K tokens, not 181K!)
  ↓
Agent builds: Auth endpoint
  ↓
Agent saves: python nexia-memory.py record --name auth --type feature ...
  ↓
Result: ✅ Auth endpoint built, saved to memory
```

### Session 2: Reuse & Build

```
User: "Build payment system"
  ↓
Agent checks: python nexia-memory.py check --task authentication
  ↓
Agent sees: ✅ Auth already built
  ↓
Agent reuses: Auth code from memory
  ↓
Agent queries: python nexia-index.py --query payment
  ↓
Agent builds: Payment system (reusing auth, massive token savings!)
  ↓
Agent saves: python nexia-memory.py record --name payment ...
  ↓
Result: ✅ Payments built, code reused, tokens saved
```

### Session 3: Maximum Reuse

```
User: "Build permissions"
  ↓
Agent views: python nexia-memory.py view --what features
  ↓
Agent sees: Auth + Payments already built
  ↓
Agent reuses: 40-50% of code
  ↓
Agent builds: Only permission-specific logic
  ↓
Agent saves: python nexia-memory.py record ...
  ↓
Result: ✅ Permissions built, massive code reuse
```

---

## All Commands

### Smart Index Queries

#### Query by Topic
```bash
python nexia-index.py --query [TOPIC] --input ./docs
```
**Example:**
```bash
python nexia-index.py --query authentication --input ./docs
```
**Result:** Returns only authentication-related sections

#### Get Database Schema
```bash
python nexia-index.py --schema --input ./docs
```
**Result:** Returns all database tables and schemas

#### Get API Endpoints
```bash
python nexia-index.py --apis --input ./docs
```
**Result:** Returns all API endpoints with methods

#### Get Specific Section
```bash
python nexia-index.py --section [DOC]:[SECTION] --input ./docs
```
**Example:**
```bash
python nexia-index.py --section api-spec.md:authentication --input ./docs
```
**Result:** Returns only that specific section

#### Build Index (One-Time)
```bash
python nexia-index.py --build --input ./docs
```
**Result:** Creates `.nexia/index.json` (permanent)

---

### Memory Management

#### Record Completed Task
```bash
python nexia-memory.py record --name [NAME] --type [TYPE] --description "[DESC]"
```
**Example:**
```bash
python nexia-memory.py record \
  --name "auth_endpoint" \
  --type "feature" \
  --description "JWT authentication with Redis cache"
```
**Types:** feature, api, fix, optimization, other

#### Check if Already Built
```bash
python nexia-memory.py check --task [TASK]
```
**Example:**
```bash
python nexia-memory.py check --task authentication
```
**Result:** Shows if already built (reuse code!)

#### View Memory
```bash
python nexia-memory.py view --what [WHAT]
```
**Options:** all, tasks, apis, schemas, artifacts, features, stats

**Example:**
```bash
python nexia-memory.py view --what features
```

#### Generate Memory Report
```bash
python nexia-memory.py report
```
**Result:** Human-readable report of all builds and savings

---

### Token Comparison

#### Generate Before/After Report
```bash
python nexia-compare.py --docs-size 707 --features 100
```
**Options:**
- `--docs-size` - Total docs size in KB (default: 707)
- `--features` - Number of features (default: 100)
- `--format` - Output format: text, json, markdown (default: text)
- `--output` - Save to file (optional)

**Example:**
```bash
python nexia-compare.py --docs-size 1000 --features 50 --format markdown --output comparison.md
```

---

## Workflows

### Workflow 1: New Project

**Day 1:**
```bash
# 1. Setup
python nexia-index.py --build --input ./docs

# 2. First feature
python nexia-index.py --query authentication
# Build auth...
python nexia-memory.py record --name auth --type feature --description "..."
```

**Day 2:**
```bash
# Agent auto-knows what to do from .nexia-config
# Queries smart, builds, saves
```

### Workflow 2: Multiple Features

**Session 1 - Build Auth:**
```bash
nexia-index.py --query auth
# Build auth endpoint
nexia-memory.py record --name auth --type feature --description "JWT auth"
```

**Session 2 - Build Payments (Reuse Auth):**
```bash
nexia-memory.py check --task auth        # ✅ Already built!
nexia-index.py --query payment
# Build payments using auth from memory
nexia-memory.py record --name payments --type feature --description "..."
```

**Session 3 - Build Permissions (Reuse Both):**
```bash
nexia-memory.py view --what features    # See auth + payments
# Reuse both
nexia-index.py --query permissions
# Build permissions with massive code reuse
nexia-memory.py record --name permissions --type feature --description "..."
```

### Workflow 3: Share Team Context

**Save context for team:**
```bash
nexia-memory.py context \
  --key "database_design" \
  --note "Using PostgreSQL with UUID primary keys"
```

**Team checks context:**
```bash
nexia-memory.py view --what context
```

---

## Troubleshooting

### Issue: "Index not found"

**Solution:**
```bash
python nexia-index.py --build --input ./docs
```

### Issue: "No docs found"

**Check:**
- Is `./docs` folder in current directory?
- Do you have `.md`, `.txt`, `.py`, `.json` files in docs?

**Fix:**
```bash
ls -la ./docs/    # Verify files exist
python nexia-index.py --build --input /full/path/to/docs
```

### Issue: "Memory file corrupted"

**Solution:**
```bash
rm .nexia/memory.json
# Memory will rebuild next time you record
```

### Issue: "Permission denied" on macOS/Linux

**Solution:**
```bash
chmod +x nexia-index.py nexia-memory.py
```

---

## FAQ

**Q: How often should I rebuild the index?**
A: Only once! Index is persistent. Rebuild only if docs change significantly.

**Q: Can I use Nexia with existing projects?**
A: Yes! Just copy 3 files and run build once.

**Q: Does Nexia work offline?**
A: Yes, 100% local. No internet needed.

**Q: Can I use with Claude Code/Cursor/Aider?**
A: Yes! Agent reads `.nexia-config` and auto-knows what to do.

**Q: How much does it cost?**
A: Free forever, MIT licensed, open source.

**Q: Can I modify the tools?**
A: Yes! MIT licensed, fork and customize as needed.

**Q: What file formats are supported?**
A: `.md`, `.txt`, `.py`, `.js`, `.json`, `.yaml`, `.yml`, `.sql`

**Q: How do I get help?**
A: Open an issue on GitHub or read README.md

---

## Keyboard Shortcuts (Tips)

### macOS/Linux

```bash
# Quick index
alias nexia-build="python nexia-index.py --build --input ./docs"
alias nexia-query="python nexia-index.py --query"
alias nexia-save="python nexia-memory.py record"
alias nexia-check="python nexia-memory.py check --task"
```

### Windows PowerShell

```powershell
function nexia-build { python nexia-index.py --build --input ./docs }
function nexia-query { python nexia-index.py --query $args }
function nexia-save { python nexia-memory.py record $args }
```

---

## Performance

**Build index:**
- 707KB docs: ~2 seconds
- 1MB docs: ~3 seconds
- CPU: Minimal (~5%)

**Query:**
- Smart query: ~100ms
- Memory check: ~50ms

**First session:** ~30 seconds total (one-time setup)
**Subsequent sessions:** ~5 seconds (agent auto-handles)

---

## Best Practices

1. **Build once** - Index is persistent
2. **Query smartly** - Use specific topics
3. **Save to memory** - After every build
4. **Check memory** - Before rebuilding
5. **View progress** - Use `--report` to see savings

---

## Next Steps

1. ✅ Read this guide
2. ✅ Run setup: `python nexia-index.py --build`
3. ✅ Start building (agent auto-knows what to do!)
4. ✅ Check results: `python nexia-memory.py report`

---

**Happy building with Nexia!** 🚀

For more: README.md | GitHub info: GITHUB.md
