# 🚀 START HERE - Autonomous Development Guide

Welcome, Claude Code! This document will get you started on building the **Distributed Compute Marketplace** project autonomously.

---

## 📚 FIRST: Read These Files (In Order)

1. **CLAUDE.md** (15 min read) - Your complete instruction manual
2. **TASKS.md** (10 min read) - Your task breakdown and tracker
3. **This file** (5 min read) - Immediate action items

---

## ✅ IMMEDIATE ACTION CHECKLIST

### Step 1: Verify Prerequisites
Check that you can access:
- [ ] Git (for version control)
- [ ] Python 3.11+ (`python --version`)
- [ ] Docker (`docker --version`)
- [ ] Internet (for fetching docs and packages)

If anything is missing, stop and alert the user.

### Step 2: Initialize Git Repository
```bash
# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env

# Logs
logs/
*.log

# Database
*.db
*.sqlite
EOF

# Initial commit
git add .gitignore
git commit -m "chore: initialize project with autonomous development guides"
```

### Step 3: Start with Task 1
Open `TASKS.md` and begin with **Task 1: Initialize project structure**

---

## 🎯 YOUR MISSION

Build a peer-to-peer compute marketplace where friends can share idle computing resources. The system must be:
- ✅ Fault-tolerant (survives node failures)
- ✅ Secure (hardened containers)
- ✅ Credit-based (fair marketplace)
- ✅ Test-driven (85% coverage minimum)
- ✅ Simple (no over-engineering)

---

## 🔄 YOUR WORKFLOW (For Every Task)

```
┌─────────────────────────────────────────┐
│ 1. READ TASKS.md - What's the task?    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. RESEARCH - Need docs? Fetch them!    │
│    Example: "Search FastAPI docs..."    │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. PLAN - Create plan in plans/ folder  │
│    Break down approach, list files       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 4. TEST - Write tests FIRST             │
│    Run: pytest tests/test_x.py -v       │
│    Confirm they FAIL (no implementation) │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 5. IMPLEMENT - Write minimal code       │
│    Keep it under 300 lines!             │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 6. VERIFY - Run all tests               │
│    pytest tests/ -v --cov=src           │
│    All green? Great! If not, fix!       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 7. FORMAT - Run black, flake8, mypy     │
│    black src/ tests/                    │
│    flake8 src/ tests/                   │
│    mypy src/ tests/                     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 8. COMMIT - Descriptive message         │
│    git add . && git commit -m "..."     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 9. UPDATE TASKS.md - Mark [✓] complete  │
│    Add timestamp and notes              │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 10. REPEAT - Next task! 🔁              │
└─────────────────────────────────────────┘
```

---

## 🚨 CRITICAL RULES (Never Break These!)

1. **TESTS FIRST, ALWAYS** - No exceptions
2. **MAX 300 LINES PER TASK** - Break larger tasks down
3. **OFFICIAL DOCS ONLY** - No assumptions, verify everything
4. **NO BROKEN CODE** - All tests must pass before commit
5. **UPDATE TASKS.MD** - After every task completion
6. **SAVE PROGRESS** - Update progress.md before context fills

---

## 📖 EXAMPLE: Your First Task Execution

Here's exactly how to execute Task 1:

### Task 1: Initialize Project Structure

**1. Read the task in TASKS.md** ✅ (You know what to do)

**2. No research needed** ✅ (It's just creating files)

**3. Create a plan** (mental is fine for this one):
```
Create these files/folders:
- requirements.txt
- README.md
- .gitignore
- .env.example
- All src/ subdirectories
- All tests/ subdirectories
- scripts/ folder
```

**4. Skip tests** (This is a structural task, no code logic)

**5. Implement**:
```bash
# Create directory structure
mkdir -p src/api src/coordinator src/agent src/database src/utils
mkdir -p tests/test_api tests/test_coordinator tests/test_agent tests/test_database tests/test_utils
mkdir -p scripts plans .claude/docs .claude/commands logs

# Create __init__.py files
touch src/__init__.py src/api/__init__.py src/coordinator/__init__.py
touch src/agent/__init__.py src/database/__init__.py src/utils/__init__.py
touch tests/__init__.py tests/test_api/__init__.py

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Docker
docker==6.1.3

# Storage
minio==7.2.0

# Security
bcrypt==4.1.1
python-jose[cryptography]==3.3.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.1

# Development
black==23.11.0
flake8==6.1.0
mypy==1.7.0

# Utilities
python-dotenv==1.0.0
psutil==5.9.6
EOF

# Create .env.example
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/compute_marketplace

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=compute-jobs

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here-change-in-production

# Coordinator
COORDINATOR_POLL_INTERVAL=5
NODE_HEARTBEAT_TIMEOUT=90

# Agent
COORDINATOR_URL=http://localhost:8000
NODE_NAME=MyNode
NODE_API_KEY=your-api-key-here
EOF

# Create basic README
cat > README.md << 'EOF'
# Distributed Compute Marketplace

A peer-to-peer compute marketplace where friends can share idle computing resources.

## Features
- Resource marketplace (list/browse available compute)
- Credit-based economy (earn/spend credits)
- Fault-tolerant job execution (survives node failures)
- Container-based isolation (Docker)
- Test-driven development (85%+ coverage)

## Architecture
- **VPS**: Coordinator, PostgreSQL, MinIO, FastAPI
- **Nodes**: Python agents running on friends' PCs
- **Network**: Tailscale VPN mesh

## Quick Start
(To be completed as project develops)

## Documentation
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [TASKS.md](TASKS.md) - Task tracker
- API Documentation: http://localhost:8000/docs

## License
MIT
EOF
```

**6. Verify** - Check all folders exist:
```bash
tree -L 2
```

**7. No formatting needed** (No code yet)

**8. Commit**:
```bash
git add .
git commit -m "chore: initialize project structure

- Create src/ and tests/ directory structure
- Add requirements.txt with all dependencies
- Add .env.example with configuration template
- Add basic README

Task: TASKS.md#1"
```

**9. Update TASKS.md**:
```markdown
- [✓] Task 1: Initialize project structure
  - Completed: 2025-10-30 10:00
  - Duration: 15 min
  - Files created: 20+
```

**10. Next task** → Task 2! 🎉

---

## 💡 TIPS FOR SUCCESS

### When Stuck
1. **Check official docs** - Search and read the actual documentation
2. **Look at examples** - Find similar code in docs/GitHub
3. **Break it down** - Task too big? Split into smaller sub-tasks
4. **Ask for help** - If truly stuck after trying, ask the user

### Context Management
- Update `progress.md` every 30 minutes
- Use `/compact` after major milestones
- Save context before long tasks
- Reference TASKS.md to restore state

### Testing Wisdom
```python
# Good test
def test_user_registration_success():
    """Test that valid user registration returns 201 with API key"""
    response = client.post("/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    assert "api_key" in response.json()
    assert len(response.json()["api_key"]) == 64

# Bad test (too vague)
def test_registration():
    response = client.post("/auth/register", json={})
    assert response.status_code == 200  # Wrong! Should be 422 for invalid data
```

### Code Quality Checklist
Before every commit:
- [ ] All tests pass (`pytest`)
- [ ] Code formatted (`black`)
- [ ] No linting errors (`flake8`)
- [ ] Type hints valid (`mypy`)
- [ ] Docstrings added (Google style)
- [ ] No debug prints or commented code
- [ ] Error handling implemented

---

## 📊 TRACK YOUR PROGRESS

### Daily
```bash
# See what's done
grep "\[✓\]" TASKS.md | wc -l

# See what's next
grep "\[ \]" TASKS.md | head -5

# Check test coverage
pytest --cov=src --cov-report=term
```

### Weekly
- Review completed tasks
- Update progress.md with weekly summary
- Check if on track for 6-week timeline

---

## 🎓 LEARNING RESOURCES

### Consult These Frequently
1. **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
2. **PostgreSQL Docs**: https://www.postgresql.org/docs/current/
3. **Docker SDK**: https://docker-py.readthedocs.io/
4. **Pytest Guide**: https://docs.pytest.org/en/stable/

### Pattern Reference
Check CLAUDE.md sections for:
- Python code style (type hints, docstrings)
- FastAPI patterns (Pydantic models, dependencies)
- Testing patterns (fixtures, parametrize)
- Database patterns (transactions, context managers)

---

## 🚦 STOP CONDITIONS

**STOP and ask user if:**
- External dependency is unavailable (VPS access, API keys)
- Requirements are ambiguous (multiple valid interpretations)
- Major architectural decision needed (impacts future tasks)
- Critical bug that blocks all progress

**DO NOT STOP for:**
- Implementation details (refer to docs)
- Minor design choices (make reasonable decision)
- Formatting questions (follow style guide)
- Testing approaches (use TDD pattern)

---

## 🎯 SUCCESS METRICS

Your goal is to complete all 55 tasks with:
- ✅ 85%+ test coverage
- ✅ All tests passing
- ✅ No critical bugs
- ✅ Working demo (Monte Carlo π estimation)
- ✅ Clean, documented code

**You can do this!** Follow the process, one task at a time. 🚀

---

## 🔥 READY TO START?

1. ✅ You've read CLAUDE.md
2. ✅ You've read TASKS.md
3. ✅ You've read this file
4. ✅ You understand the workflow

**Now execute Task 1 from TASKS.md!**

```bash
# Your first command
mkdir -p src/api src/coordinator src/agent src/database src/utils
```

Good luck! The user is counting on you to build this autonomously. Make them proud! 💪

---

**Last Updated**: 2025-10-30
**Version**: 1.0
**Next Action**: Execute Task 1 from TASKS.md
