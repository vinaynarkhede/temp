# 🚀 DISTRIBUTED COMPUTE MARKETPLACE - AUTONOMOUS DEVELOPMENT GUIDE

This file provides comprehensive guidance for Claude Code to autonomously develop a peer-to-peer compute marketplace where friends can share idle computing resources.

---

## 🚨 CRITICAL RULES FOR AUTONOMOUS DEVELOPMENT

### Rule 1: Official Documentation ONLY
- **ALWAYS** consult official documentation before implementing any library, framework, or tool
- **NEVER** assume API usage - verify with official docs first
- When encountering new dependencies, use web search to fetch official documentation
- Store frequently referenced docs in `.claude/docs/` for quick access
- Official sources priority: Python docs → FastAPI docs → PostgreSQL docs → Docker docs → Tailscale docs

### Rule 2: Test-Driven Development (TDD) - MANDATORY
- **WRITE TESTS FIRST** before any implementation code
- For every feature, follow this sequence:
  1. Write failing tests
  2. Run tests to confirm they fail
  3. Implement minimal code to pass tests
  4. Refactor if needed
  5. Commit only after all tests pass
- Test coverage target: **85% minimum**
- Use pytest for Python code
- Never skip tests - if time-constrained, reduce feature scope instead

### Rule 3: One-Shot Task Sizing
- **Maximum code generation per task: 300 lines**
- If a task requires more than 300 lines, break it into sub-tasks
- One task = One atomic, testable unit of functionality
- Each task must be completable in a single LLM response
- Update TASKS.md after completing each task

### Rule 4: No Breaking Changes
- **ALWAYS** run full test suite before committing
- Verify existing functionality still works after changes
- Use `git diff` to review changes before commit
- If tests fail, fix immediately - never commit broken code
- Rollback if integration breaks existing features

### Rule 5: Progress Tracking
- Update TASKS.md after every completed task
- Mark tasks as: `[ ]` TODO, `[>]` IN_PROGRESS, `[✓]` COMPLETED, `[✗]` BLOCKED
- Add blockers/notes in TASKS.md when stuck
- Commit TASKS.md updates with code commits
- Review TASKS.md at start of each session

### Rule 6: Context Management
- Save progress to `progress.md` before context window fills
- Use `/compact` command after completing major milestones
- Clear context with `/clear` between unrelated tasks
- Reference TASKS.md and progress.md to restore context

### Rule 7: Simplicity Over Complexity
- Choose the simplest solution that works
- Avoid premature optimization
- No unnecessary abstractions or over-engineering
- Plain Python > complex frameworks
- Direct SQL > ORM complexity (use raw queries when simpler)

---

## 🎯 PROJECT CONTEXT

### Project Vision
A **peer-to-peer compute marketplace** where friends can list idle computing resources (CPU, RAM, storage) and others can request/rent these resources to run containerized jobs. Think "Airbnb for CPU power" among a trusted friend group.

### Key Differentiators
- **Friend-to-friend marketplace** (not public cloud)
- **Dual credit system**: paid (earn/spend credits) OR donation (free, provider still earns credits)
- **Fault-tolerant**: Job chunking with automatic reallocation if nodes fail
- **Container-based**: All jobs run in hardened Docker containers
- **Resource-aware scheduling**: Match job requirements to available compute

### Primary Demo Use Case
**Monte Carlo π Estimation** - Demonstrates linear speedup with distributed computing:
- User submits: "Estimate π with 100M samples"
- System splits into 4 chunks of 25M each
- Runs on 4 nodes simultaneously → 4x faster
- Aggregates results for final estimate
- **Highly demonstrable** for interviews/portfolio

### Technology Stack (FINAL - DO NOT CHANGE)
- **Language**: Python 3.11+ (only)
- **API Framework**: FastAPI (REST API)
- **Database**: PostgreSQL (single DB for everything - no Redis, no message queues)
- **Storage**: MinIO (S3-compatible object storage)
- **Containers**: Docker (via docker-py library)
- **Networking**: Tailscale (VPN mesh)
- **Coordinator**: Python background service (simple loop)
- **Node Agent**: Python daemon (heartbeat + Docker execution)
- **VPS**: DigitalOcean/Hetzner ($5-10/mo for coordinator)

### Architecture Overview
```
VPS (Coordinator):
├── PostgreSQL (all data)
├── FastAPI (REST API)
├── MinIO (file storage)
└── Coordinator (background scheduler)

Friend Nodes:
├── Python Agent (register, heartbeat, run jobs)
└── Docker (container execution)

Network: Tailscale VPN mesh
```

---

## 📋 DEVELOPMENT WORKFLOW

### Phase 1 Pattern: Research → Plan → Implement → Test → Commit

#### Step 1: Research (ALWAYS DO THIS FIRST)
```bash
# Before implementing anything new, research using official docs
claude -p "Search official FastAPI documentation for WebSocket implementation"
claude -p "Fetch PostgreSQL documentation for JSON column types"
```
- Save relevant docs to `.claude/docs/[library-name].md`
- Reference saved docs in code comments

#### Step 2: Plan (CREATE DETAILED PLAN)
- Read TASKS.md to understand current task
- Break task into sub-tasks (each <300 lines)
- Write plan in `plans/[task-name].md`
- Include: approach, files to modify, tests needed, edge cases

#### Step 3: Write Tests FIRST
```python
# tests/test_feature.py
def test_user_registration():
    """Test that users can register with valid credentials"""
    # Arrange
    user_data = {"username": "alice", "email": "alice@example.com", "password": "secure123"}

    # Act
    response = client.post("/auth/register", json=user_data)

    # Assert
    assert response.status_code == 201
    assert "api_key" in response.json()
```
- Run tests: `pytest tests/test_feature.py -v`
- Confirm they fail (since feature not implemented yet)

#### Step 4: Implement Feature (MINIMAL CODE)
- Write only enough code to pass tests
- Follow code style guidelines (see below)
- Add docstrings to all functions
- Handle errors explicitly

#### Step 5: Verify Tests Pass
```bash
# Run specific test file
pytest tests/test_feature.py -v

# Run full test suite
pytest tests/ -v --cov=src --cov-report=html

# Check coverage
open htmlcov/index.html
```

#### Step 6: Commit with Descriptive Message
```bash
git add .
git commit -m "feat: implement user registration with API key generation

- Add POST /auth/register endpoint
- Generate unique API keys with secrets module
- Hash passwords with bcrypt
- Store users in PostgreSQL users table
- Add validation for email format and password strength
- Tests: 5 new tests, 100% coverage for auth module

Task: TASKS.md#3"
```

#### Step 7: Update TASKS.md
```markdown
- [✓] Task 3: Implement user registration
  - Completed: 2025-10-30
  - Tests: 5 passing
  - Files: src/api/auth.py, tests/test_auth.py
```

---

## 🔧 CODE STYLE & STANDARDS

### Python Style Guide
```python
# Use type hints everywhere
def calculate_credits(cpu_cores: int, ram_gb: float, duration_hours: float) -> int:
    """
    Calculate total credits for resource usage.

    Args:
        cpu_cores: Number of CPU cores requested
        ram_gb: Amount of RAM in gigabytes
        duration_hours: Duration of job in hours

    Returns:
        Total credits cost

    Raises:
        ValueError: If any parameter is negative
    """
    if cpu_cores < 0 or ram_gb < 0 or duration_hours < 0:
        raise ValueError("All parameters must be non-negative")

    CREDIT_WEIGHTS = {'cpu_core': 10, 'ram_gb': 2}
    hourly_cost = (cpu_cores * CREDIT_WEIGHTS['cpu_core'] +
                   ram_gb * CREDIT_WEIGHTS['ram_gb'])
    return int(hourly_cost * duration_hours)
```

### Rules:
- **Type hints**: Required for all function parameters and returns
- **Docstrings**: Required for all public functions (Google style)
- **Error handling**: Explicit error handling - no silent failures
- **Logging**: Use `logging` module, not print statements
- **Constants**: UPPERCASE_WITH_UNDERSCORES at module level
- **Private functions**: Prefix with underscore `_private_function()`
- **Line length**: Max 100 characters
- **Imports**: Grouped (stdlib, third-party, local) with blank lines between

### FastAPI Patterns
```python
# Use Pydantic models for request/response validation
from pydantic import BaseModel, Field, validator

class JobSubmission(BaseModel):
    docker_image: str = Field(..., description="Docker image to run")
    cpu_cores: int = Field(ge=1, le=32, description="CPU cores needed")
    ram_gb: float = Field(ge=0.5, le=128, description="RAM in GB")

    @validator('docker_image')
    def validate_image(cls, v):
        if not v.startswith(('python:', 'ubuntu:', 'alpine:')):
            raise ValueError("Image must be from approved base images")
        return v

# Use dependency injection for database sessions
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/jobs/submit")
async def submit_job(job: JobSubmission, db = Depends(get_db)):
    # Implementation here
    pass
```

### Database Patterns
```python
# Use context managers for transactions
from contextlib import contextmanager

@contextmanager
def transaction(db):
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Example usage
with transaction(db) as session:
    user = User(username="alice")
    session.add(user)
    # Auto-commits on success, auto-rolls back on error
```

### Testing Patterns
```python
# Use fixtures for common setup
import pytest

@pytest.fixture
def client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from src.api.main import app
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session for testing"""
    # Setup: Create test database
    engine = create_test_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    # Teardown: Clean up
    db.close()
    drop_test_database()

# Use parametrize for multiple test cases
@pytest.mark.parametrize("cpu_cores,ram_gb,expected_credits", [
    (4, 8, 56),   # 4*10 + 8*2 = 56
    (2, 4, 28),   # 2*10 + 4*2 = 28
    (8, 16, 112), # 8*10 + 16*2 = 112
])
def test_credit_calculation(cpu_cores, ram_gb, expected_credits):
    result = calculate_credits_per_hour(cpu_cores, ram_gb)
    assert result == expected_credits
```

---

## 📦 PROJECT STRUCTURE

```
distributed-compute-marketplace/
├── CLAUDE.md                 # This file
├── TASKS.md                  # Task tracker (update after each task)
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── docker-compose.yml        # VPS services (PostgreSQL, MinIO)
│
├── src/
│   ├── __init__.py
│   ├── api/                  # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app initialization
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── jobs.py          # Job management endpoints
│   │   ├── resources.py     # Resource marketplace endpoints
│   │   └── models.py        # Pydantic models
│   │
│   ├── coordinator/         # Background scheduler service
│   │   ├── __init__.py
│   │   ├── main.py         # Coordinator main loop
│   │   ├── scheduler.py    # Job scheduling logic
│   │   └── health.py       # Node health monitoring
│   │
│   ├── agent/              # Node agent (runs on friend PCs)
│   │   ├── __init__.py
│   │   ├── main.py        # Agent main loop
│   │   ├── docker_runner.py # Docker container management
│   │   └── heartbeat.py   # Heartbeat sender
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schema.sql     # Database schema
│   │   └── connection.py  # Database connection handling
│   │
│   └── utils/
│       ├── __init__.py
│       ├── credits.py     # Credit calculation logic
│       ├── security.py    # Container security hardening
│       └── storage.py     # MinIO client wrapper
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration and fixtures
│   ├── test_api/
│   ├── test_coordinator/
│   ├── test_agent/
│   └── test_utils/
│
├── scripts/
│   ├── install_node.sh    # One-command node agent installer
│   ├── setup_vps.sh       # VPS setup script
│   └── demo_monte_carlo.py # Monte Carlo demo job
│
├── plans/                 # Task implementation plans (create per task)
├── progress.md           # Current progress notes
└── .claude/
    ├── commands/         # Custom Claude Code commands
    └── docs/            # Downloaded official documentation
```

---

## 🗄️ DATABASE SCHEMA

### Core Tables (6 tables total - KEEP IT SIMPLE)

```sql
-- users: User accounts
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    credit_balance INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- nodes: Friend machines offering compute
CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    owner_id INT REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    tailscale_ip VARCHAR(45) NOT NULL,
    cpu_cores INT NOT NULL,
    ram_gb FLOAT NOT NULL,
    storage_gb FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'offline', -- online/offline/maintenance
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- resource_offers: Available compute for rent
CREATE TABLE resource_offers (
    id SERIAL PRIMARY KEY,
    node_id INT REFERENCES nodes(id) ON DELETE CASCADE,
    cpu_cores_available INT NOT NULL,
    ram_gb_available FLOAT NOT NULL,
    storage_gb_available FLOAT NOT NULL,
    offer_type VARCHAR(20) NOT NULL, -- 'paid' or 'free'
    approval_policy VARCHAR(20) DEFAULT 'manual', -- auto_all/auto_friends/manual
    trusted_users INT[], -- Array of user IDs for auto-approval
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- jobs: User-submitted compute jobs
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    owner_id INT REFERENCES users(id) ON DELETE CASCADE,
    docker_image VARCHAR(255) NOT NULL,
    total_chunks INT NOT NULL,
    completed_chunks INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending/running/completed/failed
    priority INT DEFAULT 5, -- 1 (highest) to 10 (lowest)
    cpu_cores_per_chunk INT NOT NULL,
    ram_gb_per_chunk FLOAT NOT NULL,
    estimated_duration_hours FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- job_chunks: Individual tasks for fault tolerance
CREATE TABLE job_chunks (
    id SERIAL PRIMARY KEY,
    job_id INT REFERENCES jobs(id) ON DELETE CASCADE,
    chunk_number INT NOT NULL,
    assigned_node_id INT REFERENCES nodes(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending/running/completed/failed
    input_data TEXT, -- JSON string or S3 path
    output_data TEXT, -- JSON string or S3 path
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INT DEFAULT 0,
    UNIQUE(job_id, chunk_number)
);

-- credit_transactions: Audit trail for credit system
CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    from_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    to_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    amount INT NOT NULL,
    transaction_type VARCHAR(50), -- 'job_payment', 'donation_reward', 'initial_credits'
    job_id INT REFERENCES jobs(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_owner ON jobs(owner_id);
CREATE INDEX idx_chunks_status ON job_chunks(status);
CREATE INDEX idx_chunks_job ON job_chunks(job_id);
CREATE INDEX idx_nodes_status ON nodes(status);
CREATE INDEX idx_transactions_user ON credit_transactions(to_user_id);
```

---

## 🧪 TESTING REQUIREMENTS

### Test Coverage Requirements
- **Minimum coverage: 85%**
- Every endpoint must have tests
- Every utility function must have tests
- Edge cases and error paths must be tested

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── test_api/
│   ├── test_auth.py        # Auth endpoints
│   ├── test_jobs.py        # Job endpoints
│   └── test_resources.py   # Resource endpoints
├── test_coordinator/
│   ├── test_scheduler.py   # Scheduling logic
│   └── test_health.py      # Health monitoring
├── test_agent/
│   ├── test_docker_runner.py
│   └── test_heartbeat.py
└── test_utils/
    ├── test_credits.py     # Credit calculations
    └── test_security.py    # Security functions
```

### Test Execution Commands
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api/test_auth.py -v

# Run tests matching pattern
pytest tests/ -k "test_auth" -v

# Run with verbose output and print statements
pytest tests/ -v -s

# Run failed tests only (after a failure)
pytest tests/ --lf -v

# Run in parallel (install pytest-xdist first)
pytest tests/ -n auto -v
```

### Test Writing Checklist
For each feature, ensure tests cover:
- ✅ Happy path (normal successful execution)
- ✅ Invalid input (wrong types, out of range)
- ✅ Missing data (required fields not provided)
- ✅ Authentication/authorization (unauthorized access)
- ✅ Database errors (connection failures, constraint violations)
- ✅ Edge cases (boundary values, empty lists, null values)
- ✅ Idempotency (repeated calls produce same result)

---

## ⚙️ COMMON COMMANDS & WORKFLOWS

### Development Setup
```bash
# Initial setup (one time)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL and MinIO with Docker Compose
docker-compose up -d

# Initialize database
python scripts/init_db.py

# Start API server (development)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start coordinator (in separate terminal)
python -m src.coordinator.main

# Start node agent (on friend PC)
python -m src.agent.main --node-name "Alice-PC" --api-key "xyz123"
```

### Testing Commands
```bash
# Format code
black src/ tests/

# Lint code
pylint src/ tests/
flake8 src/ tests/

# Type check
mypy src/ tests/

# Run tests
pytest tests/ -v --cov=src

# Security audit
bandit -r src/
```

### Git Workflow
```bash
# Before starting new task
git checkout -b feature/task-name

# After completing task
git add .
git commit -m "feat: descriptive message (see TASKS.md#N)"
git push origin feature/task-name

# After tests pass on CI
git checkout main
git merge feature/task-name
git push origin main
```

### Debugging
```bash
# View API logs
tail -f logs/api.log

# View coordinator logs
tail -f logs/coordinator.log

# Connect to PostgreSQL
docker exec -it postgres psql -U postgres -d compute_marketplace

# Check MinIO buckets
mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc ls myminio/
```

---

## 📚 OFFICIAL DOCUMENTATION REFERENCES

### Must Reference Before Implementation
1. **FastAPI**: https://fastapi.tiangolo.com/
2. **PostgreSQL**: https://www.postgresql.org/docs/
3. **Docker SDK for Python**: https://docker-py.readthedocs.io/
4. **Pydantic**: https://docs.pydantic.dev/
5. **SQLAlchemy**: https://docs.sqlalchemy.org/
6. **Pytest**: https://docs.pytest.org/
7. **MinIO Python Client**: https://min.io/docs/minio/linux/developers/python/API.html
8. **Tailscale**: https://tailscale.com/kb/

### Fetching Documentation
When implementing a new feature:
```bash
# Example: Before implementing WebSocket
claude -p "Fetch and summarize FastAPI WebSocket documentation from https://fastapi.tiangolo.com/advanced/websockets/"

# Save to local docs
# Copy relevant parts to .claude/docs/fastapi-websockets.md
```

---

## 🎯 SUCCESS CRITERIA PER TASK

Each task is considered complete ONLY when ALL criteria are met:

### Criteria Checklist
- [ ] **Tests written FIRST** (before implementation)
- [ ] **Tests passing** (100% pass rate for new tests)
- [ ] **Coverage met** (>=85% for modified code)
- [ ] **Code formatted** (black, flake8 pass)
- [ ] **Type checked** (mypy passes with no errors)
- [ ] **Documentation updated** (docstrings, README if needed)
- [ ] **No regressions** (all existing tests still pass)
- [ ] **TASKS.md updated** (mark task complete, add notes)
- [ ] **Committed to git** (with descriptive message)
- [ ] **Manual verification** (if applicable, test in running system)

### Verification Script
Create and run this for each task:
```bash
#!/bin/bash
# verify_task.sh - Run before marking task complete

echo "🧪 Running tests..."
pytest tests/ -v --cov=src --cov-report=term || exit 1

echo "🎨 Checking code format..."
black --check src/ tests/ || exit 1

echo "🔍 Linting..."
flake8 src/ tests/ || exit 1

echo "🔒 Type checking..."
mypy src/ tests/ || exit 1

echo "✅ All checks passed! Task ready for completion."
```

---

## 🔄 TASK BREAKDOWN STRATEGY

### How to Break Tasks into One-Shottable Units

#### ❌ Bad Task (Too Large)
```markdown
- [ ] Implement job submission system
```
This is too broad - involves API, database, validation, credits, etc.

#### ✅ Good Task Breakdown
```markdown
- [ ] Task 10: Create Pydantic models for job submission
  - File: src/api/models.py
  - Lines: ~50
  - Tests: tests/test_api/test_models.py
  - Duration: 15 min

- [ ] Task 11: Add job submission endpoint (no business logic)
  - File: src/api/jobs.py
  - Lines: ~80
  - Tests: tests/test_api/test_jobs_endpoint.py
  - Duration: 20 min

- [ ] Task 12: Implement credit checking logic
  - File: src/utils/credits.py
  - Lines: ~100
  - Tests: tests/test_utils/test_credits.py
  - Duration: 25 min
```

### Task Sizing Guidelines
- **Tiny (50-100 lines)**: Single utility function, simple model
- **Small (100-150 lines)**: Single endpoint, basic logic class
- **Medium (150-250 lines)**: Complex logic, multiple related functions
- **Large (250-300 lines)**: MAXIMUM - integrated feature with multiple components
- **Too Large (>300 lines)**: MUST BE SPLIT - break into smaller tasks

### Task Template
```markdown
- [ ] Task #N: [Verb] [Specific Feature]
  - **File(s)**: src/path/to/file.py
  - **Estimated Lines**: ~150
  - **Dependencies**: Task #M (must be completed first)
  - **Tests Required**:
    - Happy path test
    - Error handling test
    - Edge case test
  - **Acceptance Criteria**:
    - [ ] Criteria 1
    - [ ] Criteria 2
  - **Notes**: Any important context or considerations
```

---

## 🚀 AUTONOMOUS OPERATION GUIDELINES

### Self-Sufficiency Principles

1. **Don't Ask Permission - Just Build**
   - Follow the plan in TASKS.md
   - Make reasonable decisions within project scope
   - Document decisions in progress.md
   - Only ask clarifying questions if project direction is ambiguous

2. **Self-Correct When Stuck**
   - If tests fail: Debug, fix, re-test
   - If approach is wrong: Rollback, try different approach
   - If dependency missing: Install it and document in requirements.txt
   - If docs unclear: Search for better examples/tutorials

3. **Continuous Verification**
   - Run tests after every code change
   - Check type hints with mypy regularly
   - Format code with black before committing
   - Review git diff before committing

4. **Context Preservation**
   - Update progress.md before context fills
   - Use /compact after major milestones
   - Reference TASKS.md to restore context
   - Save intermediate work to git branches

### When to Seek Clarification
Only ask the user when:
- Project requirements are genuinely ambiguous
- Multiple valid approaches exist and choice significantly impacts architecture
- External dependencies (like VPS access) are needed
- Security/privacy concerns arise

Do NOT ask about:
- Implementation details (refer to official docs)
- Coding patterns (follow style guide in this file)
- Testing approaches (use TDD pattern described above)
- Minor decisions (make reasonable choice and document)

---

## 🔐 SECURITY HARDENING CHECKLIST

For every Docker container execution:
```python
# MANDATORY security configuration
container_config = {
    'image': job.docker_image,
    'command': job.command,

    # Security hardening
    'user': '1000:1000',                    # Non-root user
    'read_only': True,                      # Read-only root filesystem
    'security_opt': ['no-new-privileges'],  # No privilege escalation
    'cap_drop': ['ALL'],                    # Drop all Linux capabilities
    'network_mode': 'none',                 # No network access

    # Resource limits
    'mem_limit': f'{job.ram_gb}g',
    'memswap_limit': f'{job.ram_gb}g',
    'cpu_quota': job.cpu_cores * 100000,
    'pids_limit': 100,

    # Storage limits
    'storage_opt': {'size': f'{job.storage_gb}G'},

    # Volume mounts (controlled)
    'volumes': {
        '/tmp/input': {'bind': '/input', 'mode': 'ro'},
        '/tmp/output': {'bind': '/output', 'mode': 'rw'}
    }
}
```

### Approved Base Images (Whitelist)
```python
APPROVED_BASE_IMAGES = [
    'python:3.11-slim',
    'python:3.11-alpine',
    'ubuntu:22.04',
    'ubuntu:24.04',
    'alpine:3.18',
    'alpine:3.19',
]

def validate_docker_image(image: str) -> bool:
    """Ensure image is from approved base images"""
    return any(image.startswith(base) for base in APPROVED_BASE_IMAGES)
```

---

## 🎓 LEARNING FROM ERRORS

### When Tests Fail
1. **Read the error message carefully** - it usually tells you exactly what's wrong
2. **Check the stack trace** - find the exact line causing the issue
3. **Reproduce manually** - run the code path in isolation
4. **Add debug logging** - print intermediate values
5. **Consult official docs** - verify API usage
6. **Check for typos** - variable names, imports, etc.
7. **Review recent changes** - use `git diff` to see what changed

### Common Mistakes to Avoid
- ❌ Skipping tests ("I'll add them later")
- ❌ Committing broken code ("I'll fix it tomorrow")
- ❌ Ignoring type errors from mypy
- ❌ Not reading official documentation
- ❌ Creating tasks >300 lines
- ❌ Not updating TASKS.md after completing work
- ❌ Forgetting to activate virtual environment
- ❌ Hardcoding credentials (use environment variables)

---

## 📞 SUPPORT & RESOURCES

### Official Documentation Priority
1. Python docs: https://docs.python.org/3/
2. FastAPI: https://fastapi.tiangolo.com/
3. PostgreSQL: https://www.postgresql.org/docs/
4. Docker SDK: https://docker-py.readthedocs.io/
5. Pytest: https://docs.pytest.org/

### Example Projects (for reference)
- FastAPI + PostgreSQL: https://github.com/tiangolo/full-stack-fastapi-postgresql
- Docker container management: https://docker-py.readthedocs.io/en/stable/containers.html
- Pytest fixtures: https://docs.pytest.org/en/stable/fixture.html

### Debugging Tips
```python
# Use Python debugger for complex issues
import pdb; pdb.set_trace()

# Use logging instead of print
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")

# Use pytest's -s flag to see print statements
pytest tests/test_file.py -v -s
```

---

## 🎯 REMEMBER: THE GOAL

Build a **working, demonstrable system** that shows:
1. ✅ Distributed computing with fault tolerance
2. ✅ Marketplace economics (credit system)
3. ✅ Resource-aware scheduling
4. ✅ Container security
5. ✅ Test-driven development
6. ✅ Clean, maintainable code

**NOT**:
- ❌ Perfect code (good enough is good enough)
- ❌ Every feature imaginable (MVP first)
- ❌ Over-engineering (simple beats complex)

---

**Last Updated**: 2025-10-30
**Version**: 1.0
**Author**: Human + Claude
**Purpose**: Autonomous development of distributed compute marketplace

---

**FINAL REMINDER**: You are capable of building this entire project autonomously. Trust the process: Research → Plan → Test → Implement → Verify → Commit. One task at a time. You got this! 🚀
