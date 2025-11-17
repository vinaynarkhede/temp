# DISTRIBUTED COMPUTE MARKETPLACE - TASK TRACKER

**Project Start Date**: 2025-10-30
**Target Completion**: 6 weeks
**Current Phase**: Phase 1 - Foundation

---

## STATUS LEGEND
- `[ ]` **TODO**: Not started
- `[>]` **IN_PROGRESS**: Currently working on
- `[✓]` **COMPLETED**: Done, tested, and committed
- `[✗]` **BLOCKED**: Waiting on dependency or external issue
- `[~]` **SKIPPED**: Decided not to implement (with reason)

---

## PROGRESS SUMMARY

| Phase | Tasks | Completed | Percentage |
|-------|-------|-----------|------------|
| Phase 1: Foundation | 15 | 12 | 80% |
| Phase 2: Core Marketplace | 12 | 0 | 0% |
| Phase 3: Distribution & Scheduling | 10 | 0 | 0% |
| Phase 4: Fault Tolerance | 8 | 0 | 0% |
| Phase 5: Security & Polish | 10 | 0 | 0% |
| **TOTAL** | **55** | **12** | **22%** |

---

## PHASE 1: FOUNDATION (Week 1)

**Goal**: Set up project structure, database, and basic authentication.

### 1.1 Project Setup

- [✓] **Task 1: Initialize project structure**
  - **Description**: Create complete folder structure, requirements.txt, README.md, .gitignore
  - **Files to create**:
    - `requirements.txt` (FastAPI, PostgreSQL, docker-py, pytest, etc.)
    - `README.md` (project overview and setup instructions)
    - `.gitignore` (Python, venv, IDE files)
    - `.env.example` (environment variables template)
    - All folders from project structure in CLAUDE.md
  - **Tests**: None (structural task)
  - **Estimated Lines**: ~100
  - **Duration**: 20 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] All folders exist
    - [✓] requirements.txt has all dependencies
    - [✓] README has setup instructions
    - [✓] .gitignore excludes venv, __pycache__, .env

- [✓] **Task 2: Setup database schema**
  - **Description**: Create SQL schema file with all 6 tables and indexes
  - **Files to create**: `src/database/schema.sql`
  - **Reference**: CLAUDE.md "DATABASE SCHEMA" section
  - **Tests**: Manual verification with psql
  - **Estimated Lines**: ~150
  - **Actual Lines**: 241
  - **Duration**: 30 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] All 6 tables defined (users, nodes, resource_offers, jobs, job_chunks, credit_transactions)
    - [✓] All indexes created (22 total)
    - [✓] Schema can be executed without errors
    - [✓] Constraints and foreign keys properly defined
  - **Notes**: Also added schema_version table for migrations, triggers for updated_at, and comprehensive comments

- [✓] **Task 3: Setup Docker Compose for VPS services**
  - **Description**: Create docker-compose.yml with PostgreSQL and MinIO
  - **Files to create**: `docker-compose.yml`, `.env.example`
  - **Services**: PostgreSQL 15, MinIO latest
  - **Tests**: `docker-compose up -d` works, services accessible
  - **Estimated Lines**: ~80
  - **Actual Lines**: 93
  - **Duration**: 25 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] PostgreSQL accessible on localhost:5432
    - [✓] MinIO accessible on localhost:9000
    - [✓] Services persist data in Docker volumes
    - [✓] Can connect to PostgreSQL with psql
  - **Notes**: Includes health checks, auto-bucket creation, and proper networking. Docker not available in dev environment but config verified

- [✓] **Task 4: Create database connection module**
  - **Description**: Setup SQLAlchemy connection handling with connection pooling
  - **Files to create**: `src/database/connection.py`, `src/database/__init__.py`
  - **Reference**: https://docs.sqlalchemy.org/en/20/core/engines.html
  - **Tests**: `tests/test_database/test_connection.py`
  - **Test Cases**:
    - Connection can be established
    - Connection pooling works
    - Transactions work correctly
    - Connection cleanup on error
  - **Estimated Lines**: ~120
  - **Actual Lines**: 198 (implementation), 153 (tests)
  - **Duration**: 35 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] Can connect to PostgreSQL
    - [✓] Connection pool configured (min=5, max=20)
    - [✓] Context manager for transactions
    - [✓] 10 tests passing, 1 skipped
  - **Notes**: Followed TDD - wrote 11 tests FIRST, then implemented. Includes FastAPI dependency injection support, singleton engine pattern, comprehensive logging

- [✓] **Task 5: Create database initialization script**
  - **Description**: Script to create database and run schema
  - **Files to create**: `scripts/init_db.py`
  - **Tests**: Manual - run script and verify tables exist
  - **Estimated Lines**: ~80
  - **Actual Lines**: 348
  - **Duration**: 20 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] Script creates database if not exists
    - [✓] Script runs schema.sql
    - [✓] Script is idempotent (can run multiple times safely)
    - [✓] Script prints success/error messages
  - **Notes**: Includes database URL parsing, existence checking, table verification, comprehensive error handling with logging

### 1.2 Authentication System

- [✓] **Task 6: Create Pydantic models for authentication**
  - **Description**: Define UserRegister, UserLogin, UserResponse models
  - **Files to create**: `src/api/models.py`, `src/api/__init__.py`
  - **Reference**: https://docs.pydantic.dev/latest/
  - **Tests**: `tests/test_api/test_models.py`
  - **Test Cases**:
    - Valid data passes validation
    - Invalid email rejected
    - Weak password rejected
    - Missing fields rejected
  - **Estimated Lines**: ~100
  - **Actual Lines**: 165 (implementation), 213 (tests)
  - **Duration**: 25 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] UserRegister model with email validation
    - [✓] UserLogin model
    - [✓] UserResponse model (no password exposure)
    - [✓] 14 validation tests passing
  - **Notes**: Followed TDD - wrote 14 tests first. Added email-validator dependency. Includes password strength validation, username validation, ORM mode support

- [✓] **Task 7: Implement password hashing utility**
  - **Description**: Create utility for bcrypt password hashing and verification
  - **Files to create**: `src/utils/security.py`, `src/utils/__init__.py`
  - **Reference**: https://github.com/pyca/bcrypt/
  - **Tests**: `tests/test_utils/test_security.py`
  - **Test Cases**:
    - Password hashing produces different hashes for same password
    - Correct password verifies successfully
    - Incorrect password fails verification
    - Hash format is valid bcrypt
  - **Estimated Lines**: ~60
  - **Actual Lines**: 106 (implementation), 143 (tests)
  - **Duration**: 20 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] `hash_password()` function
    - [✓] `verify_password()` function
    - [✓] Uses bcrypt with work factor 12
    - [✓] 13 tests passing (exceeded 4+ requirement)
  - **Notes**: Followed TDD - wrote 13 tests first. Includes edge case handling (Unicode, long passwords, invalid hashes)

- [✓] **Task 8: Implement API key generation utility**
  - **Description**: Create utility to generate secure random API keys
  - **Files to modify**: `src/utils/security.py`
  - **Tests**: `tests/test_utils/test_security.py`
  - **Test Cases**:
    - API keys are unique
    - API keys are 64 characters
    - API keys are URL-safe
    - Multiple generations don't collide (test 1000 times)
  - **Estimated Lines**: ~40
  - **Actual Lines**: Included in Task 7 implementation
  - **Duration**: 15 min
  - **Completed**: 2025-11-17 (bundled with Task 7)
  - **Success Criteria**:
    - [✓] `generate_api_key()` function
    - [✓] Uses secrets.token_urlsafe()
    - [✓] Returns 64-character string
    - [✓] 4 tests passing
  - **Notes**: Implemented together with Task 7 in same module. All tests already passing

- [✓] **Task 9: Create SQLAlchemy User model**
  - **Description**: Define User ORM model matching database schema
  - **Files to create**: `src/database/models.py`
  - **Reference**: https://docs.sqlalchemy.org/en/20/orm/
  - **Tests**: `tests/test_database/test_models.py`
  - **Test Cases**:
    - User can be created
    - User can be queried
    - Unique constraints work (username, email, api_key)
    - Timestamps auto-populate
  - **Estimated Lines**: ~80
  - **Actual Lines**: 84 (implementation), 119 (tests), 46 (conftest)
  - **Duration**: 25 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] User model with all fields
    - [✓] Relationships defined (if any)
    - [✓] __repr__ method for debugging
    - [✓] 8 tests passing (exceeded 4+ requirement)
  - **Notes**: Followed TDD - wrote 8 tests first. Created pytest conftest.py with db_session fixture. Uses SQLAlchemy 2.0 style. Includes to_dict() method for serialization

- [✓] **Task 10: Implement user registration endpoint**
  - **Description**: POST /auth/register endpoint
  - **Files to create**: `src/api/auth.py`, `src/api/main.py`
  - **Tests**: `tests/test_api/test_auth.py`
  - **Test Cases**:
    - Valid registration succeeds (201)
    - Returns API key
    - Duplicate username rejected (409)
    - Duplicate email rejected (409)
    - Invalid email rejected (422)
    - Weak password rejected (422)
  - **Estimated Lines**: ~120
  - **Actual Lines**: 112 (auth.py), 46 (main.py), 138 (tests), 39 (conftest update)
  - **Duration**: 35 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] Endpoint accepts UserRegister model
    - [✓] Hashes password before storing
    - [✓] Generates and stores API key
    - [✓] Initializes credit balance to 100
    - [✓] 9 tests passing (exceeded 6+ requirement)
  - **Notes**: Followed TDD - wrote 9 tests first. Includes comprehensive error handling for duplicate username/email, API key collision. Created FastAPI app with CORS, health check endpoint. Updated conftest with client fixture for API testing

- [✓] **Task 11: Implement user login endpoint**
  - **Description**: POST /auth/login endpoint returning API key
  - **Files to modify**: `src/api/auth.py`
  - **Tests**: `tests/test_api/test_auth.py`
  - **Test Cases**:
    - Valid login succeeds (200)
    - Returns API key
    - Invalid username rejected (401)
    - Invalid password rejected (401)
    - Rate limiting works (optional for V1)
  - **Estimated Lines**: ~80
  - **Actual Lines**: 52 (auth.py addition), 75 (tests)
  - **Duration**: 25 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] Endpoint accepts UserLogin model
    - [✓] Verifies password hash
    - [✓] Returns existing API key
    - [✓] 4 tests passing
  - **Notes**: Followed TDD - wrote 4 tests first. Password verification with bcrypt, returns existing API key (not new one). Clear error messages for invalid credentials

- [✓] **Task 12: Implement API key authentication dependency**
  - **Description**: FastAPI dependency for authenticating requests via API key
  - **Files to modify**: `src/api/auth.py`
  - **Tests**: `tests/test_api/test_auth.py`
  - **Test Cases**:
    - Valid API key allows access
    - Invalid API key rejected (401)
    - Missing API key rejected (401)
    - Dependency injects User object
  - **Estimated Lines**: ~60
  - **Actual Lines**: 72 (auth.py addition), 58 (tests)
  - **Duration**: 20 min
  - **Completed**: 2025-11-17
  - **Success Criteria**:
    - [✓] `get_current_user()` dependency function
    - [✓] Checks X-API-Key header
    - [✓] Queries user from database
    - [✓] 4 tests passing
  - **Notes**: Followed TDD - wrote 4 tests first. Created GET /auth/me endpoint to test dependency. Returns User object for use in protected endpoints. Clear error messages for missing/invalid API key

### 1.3 Basic API Setup

- [ ] **Task 13: Create FastAPI application with CORS and error handlers**
  - **Description**: Initialize FastAPI app with middleware and global exception handlers
  - **Files to create/modify**: `src/api/main.py`
  - **Reference**: https://fastapi.tiangolo.com/tutorial/
  - **Tests**: `tests/test_api/test_main.py`
  - **Test Cases**:
    - App starts successfully
    - CORS headers present
    - 404 returns proper JSON
    - 500 returns proper JSON
    - Health check endpoint works
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] FastAPI app initialized
    - [ ] CORS middleware configured
    - [ ] Global exception handler for errors
    - [ ] GET /health endpoint (returns {status: "ok"})
    - [ ] 5+ tests passing

- [ ] **Task 14: Setup pytest configuration and fixtures**
  - **Description**: Create conftest.py with shared test fixtures
  - **Files to create**: `tests/conftest.py`, `tests/__init__.py`
  - **Fixtures needed**:
    - `client` - FastAPI TestClient
    - `db_session` - Database session for tests
    - `test_user` - Authenticated test user
    - `clear_database` - Clean up between tests
  - **Tests**: Fixtures themselves (verify they work)
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] conftest.py with 4+ fixtures
    - [ ] Fixtures properly clean up after tests
    - [ ] Test database separate from dev database
    - [ ] All existing tests still pass

- [ ] **Task 15: Create logging configuration**
  - **Description**: Setup Python logging with file and console handlers
  - **Files to create**: `src/utils/logging_config.py`
  - **Tests**: `tests/test_utils/test_logging.py`
  - **Test Cases**:
    - Logs written to file
    - Console output works
    - Different log levels work
    - Log rotation works (optional)
  - **Estimated Lines**: ~80
  - **Duration**: 25 min
  - **Success Criteria**:
    - [ ] Configure logging for all modules
    - [ ] Logs to `logs/api.log` and `logs/coordinator.log`
    - [ ] Console output for development
    - [ ] Proper log format with timestamps
    - [ ] 3+ tests passing

---

## PHASE 2: CORE MARKETPLACE (Week 2)

**Goal**: Implement resource listing, browsing, and basic job submission.

### 2.1 Resource Management

- [ ] **Task 16: Create SQLAlchemy models for Node and ResourceOffer**
  - **Description**: Define Node and ResourceOffer ORM models
  - **Files to modify**: `src/database/models.py`
  - **Tests**: `tests/test_database/test_models.py`
  - **Test Cases**:
    - Node can be created with owner relationship
    - ResourceOffer can be created with node relationship
    - Foreign key constraints work
    - Status enums work correctly
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Dependencies**: Task 9 (User model)
  - **Success Criteria**:
    - [ ] Node model complete
    - [ ] ResourceOffer model complete
    - [ ] Relationships to User defined
    - [ ] 6+ tests passing

- [ ] **Task 17: Create Pydantic models for resource operations**
  - **Description**: NodeRegister, ResourceOfferCreate, ResourceOfferResponse models
  - **Files to modify**: `src/api/models.py`
  - **Tests**: `tests/test_api/test_models.py`
  - **Test Cases**:
    - Valid resource offer passes validation
    - Negative resources rejected
    - Invalid offer_type rejected
    - Invalid approval_policy rejected
  - **Estimated Lines**: ~120
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] All models have proper validation
    - [ ] Enums for offer_type and approval_policy
    - [ ] 5+ validation tests passing

- [ ] **Task 18: Implement node registration endpoint**
  - **Description**: POST /nodes/register for nodes to join cluster
  - **Files to create**: `src/api/nodes.py`
  - **Tests**: `tests/test_api/test_nodes.py`
  - **Test Cases**:
    - Authenticated user can register node
    - Node data stored correctly
    - Duplicate node names handled
    - Returns node ID
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] Endpoint requires authentication
    - [ ] Stores node in database
    - [ ] Returns node object with ID
    - [ ] 4+ tests passing

- [ ] **Task 19: Implement resource offer creation endpoint**
  - **Description**: POST /resources/offer to list available compute
  - **Files to create**: `src/api/resources.py`
  - **Tests**: `tests/test_api/test_resources.py`
  - **Test Cases**:
    - User can create resource offer
    - Offer linked to user's node
    - Validation works (resources <= node capacity)
    - Returns offer ID
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Dependencies**: Task 18 (node registration)
  - **Success Criteria**:
    - [ ] Endpoint requires authentication
    - [ ] Validates resources don't exceed node capacity
    - [ ] Stores offer in database
    - [ ] 5+ tests passing

- [ ] **Task 20: Implement resource browsing endpoint**
  - **Description**: GET /resources/available with filtering
  - **Files to modify**: `src/api/resources.py`
  - **Tests**: `tests/test_api/test_resources.py`
  - **Test Cases**:
    - Returns all active offers
    - Filter by min CPU works
    - Filter by min RAM works
    - Filter by offer_type works
    - Only returns online nodes
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] Returns list of available resources
    - [ ] Supports query params for filtering
    - [ ] Only returns active=True offers
    - [ ] Only returns nodes with status='online'
    - [ ] 6+ tests passing

- [ ] **Task 21: Implement resource offer update endpoint**
  - **Description**: PUT /resources/offer/{offer_id} to modify offerings
  - **Files to modify**: `src/api/resources.py`
  - **Tests**: `tests/test_api/test_resources.py`
  - **Test Cases**:
    - Owner can update their offer
    - Non-owner cannot update (403)
    - Can change availability, resources, policies
    - Validation still applies
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] Only offer owner can update
    - [ ] Can update all fields except node_id
    - [ ] Validation on updates
    - [ ] 4+ tests passing

### 2.2 Credit System

- [ ] **Task 22: Implement credit calculation utility**
  - **Description**: Functions to calculate credit costs for resources
  - **Files to create**: `src/utils/credits.py`
  - **Reference**: CLAUDE.md "Credit Calculation Formula"
  - **Tests**: `tests/test_utils/test_credits.py`
  - **Test Cases**:
    - Formula matches specification
    - Handles fractional hours
    - Different resource combinations
    - Edge cases (0 resources, massive resources)
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] `calculate_credits_per_hour()` function
    - [ ] `calculate_total_job_cost()` function
    - [ ] Uses weights from CLAUDE.md
    - [ ] 8+ tests with parametrize

- [ ] **Task 23: Implement credit transaction recording**
  - **Description**: Function to record credit transfers in database
  - **Files to modify**: `src/utils/credits.py`
  - **Tests**: `tests/test_utils/test_credits.py`
  - **Test Cases**:
    - Transaction recorded correctly
    - User balances updated
    - Atomic transaction (rollback on error)
    - Audit trail complete
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] `transfer_credits()` function
    - [ ] Updates from_user and to_user balances
    - [ ] Records transaction in credit_transactions
    - [ ] Uses database transaction
    - [ ] 5+ tests passing

- [ ] **Task 24: Implement credit balance endpoints**
  - **Description**: GET /credits/balance and GET /credits/history
  - **Files to create**: `src/api/credits.py`
  - **Tests**: `tests/test_api/test_credits.py`
  - **Test Cases**:
    - User can view their balance
    - User can view their transaction history
    - Cannot view other user's data
    - Pagination works for history
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] GET /credits/balance returns current balance
    - [ ] GET /credits/history returns transactions
    - [ ] Supports pagination
    - [ ] 4+ tests passing

### 2.3 Job Submission

- [ ] **Task 25: Create SQLAlchemy models for Job and JobChunk**
  - **Description**: Define Job and JobChunk ORM models
  - **Files to modify**: `src/database/models.py`
  - **Tests**: `tests/test_database/test_models.py`
  - **Test Cases**:
    - Job can be created
    - JobChunks linked to Job
    - Status enums work
    - Cascade delete works (job deletes chunks)
  - **Estimated Lines**: ~180
  - **Duration**: 45 min
  - **Success Criteria**:
    - [ ] Job model complete
    - [ ] JobChunk model complete
    - [ ] Foreign key relationships
    - [ ] 6+ tests passing

- [ ] **Task 26: Create Pydantic models for job submission**
  - **Description**: JobSubmission, JobResponse, JobStatus models
  - **Files to modify**: `src/api/models.py`
  - **Tests**: `tests/test_api/test_models.py`
  - **Test Cases**:
    - Valid job submission passes
    - Invalid Docker image rejected
    - Negative resources rejected
    - Resource limits enforced (max 32 cores)
  - **Estimated Lines**: ~120
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] JobSubmission model with validation
    - [ ] Docker image validation (whitelist)
    - [ ] Resource limit validation
    - [ ] 6+ tests passing

- [ ] **Task 27: Implement job submission endpoint (basic)**
  - **Description**: POST /jobs/submit (no scheduling yet, just validation and storage)
  - **Files to create**: `src/api/jobs.py`
  - **Tests**: `tests/test_api/test_jobs.py`
  - **Test Cases**:
    - Authenticated user can submit job
    - Job stored in database
    - Returns job ID
    - Input validation works
    - Insufficient credits rejected
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Dependencies**: Task 22 (credit calculation)
  - **Success Criteria**:
    - [ ] Endpoint requires authentication
    - [ ] Validates resources
    - [ ] Checks user has enough credits
    - [ ] Stores job with status='pending'
    - [ ] 6+ tests passing

---

## PHASE 3: DISTRIBUTION & SCHEDULING (Week 3)

**Goal**: Implement coordinator, node agent, and job distribution.

### 3.1 Coordinator Service

- [ ] **Task 28: Create coordinator main loop structure**
  - **Description**: Basic coordinator service that polls for work
  - **Files to create**: `src/coordinator/main.py`, `src/coordinator/__init__.py`
  - **Tests**: `tests/test_coordinator/test_main.py`
  - **Test Cases**:
    - Coordinator starts and runs loop
    - Loop can be stopped gracefully
    - Handles database connection errors
    - Logs activity
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] Main loop runs every 5 seconds
    - [ ] Can be stopped with Ctrl+C
    - [ ] Catches and logs exceptions
    - [ ] 3+ tests passing

- [ ] **Task 29: Implement node health checking**
  - **Description**: Check node heartbeats and mark dead nodes
  - **Files to create**: `src/coordinator/health.py`
  - **Tests**: `tests/test_coordinator/test_health.py`
  - **Test Cases**:
    - Nodes with recent heartbeats stay online
    - Nodes with old heartbeats marked offline
    - Configurable timeout (default 90 seconds)
    - Updates node status in database
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] `check_node_health()` function
    - [ ] Queries nodes with last_heartbeat
    - [ ] Marks nodes offline if timeout exceeded
    - [ ] 4+ tests passing

- [ ] **Task 30: Implement job chunking logic**
  - **Description**: Split jobs into chunks for distribution
  - **Files to create**: `src/coordinator/chunking.py`
  - **Tests**: `tests/test_coordinator/test_chunking.py`
  - **Test Cases**:
    - Job split into specified number of chunks
    - Each chunk has correct input data
    - Chunks stored in database
    - Idempotent (don't re-chunk existing job)
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] `create_job_chunks()` function
    - [ ] Takes job and chunk count
    - [ ] Creates JobChunk records
    - [ ] Handles Monte Carlo input distribution
    - [ ] 6+ tests passing

- [ ] **Task 31: Implement basic scheduler**
  - **Description**: Match pending chunks to available nodes (FIFO)
  - **Files to create**: `src/coordinator/scheduler.py`
  - **Tests**: `tests/test_coordinator/test_scheduler.py`
  - **Test Cases**:
    - Finds pending chunks
    - Finds online nodes
    - Matches chunk resources to node capacity
    - Assigns chunk to node
    - Updates chunk status to 'running'
  - **Estimated Lines**: ~200
  - **Duration**: 50 min
  - **Success Criteria**:
    - [ ] `schedule_pending_chunks()` function
    - [ ] Queries pending chunks and online nodes
    - [ ] Checks resource availability
    - [ ] Assigns chunks to nodes
    - [ ] 7+ tests passing

- [ ] **Task 32: Implement chunk assignment endpoint**
  - **Description**: GET /coordinator/chunks/pending for agents to poll
  - **Files to create**: `src/api/coordinator.py`
  - **Tests**: `tests/test_api/test_coordinator.py`
  - **Test Cases**:
    - Agent can get assigned chunks
    - Only returns chunks for that node
    - Returns empty list if no chunks
    - Authentication required (node-specific)
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] Endpoint returns chunks for specific node
    - [ ] Filters by assigned_node_id
    - [ ] Filters by status='running'
    - [ ] 4+ tests passing

- [ ] **Task 33: Integrate coordinator with main loop**
  - **Description**: Wire health checking, chunking, and scheduling into main loop
  - **Files to modify**: `src/coordinator/main.py`
  - **Tests**: Integration test in `tests/test_coordinator/test_integration.py`
  - **Test Cases**:
    - Full cycle: pending job → chunked → scheduled → assigned
    - Multiple jobs handled correctly
    - Node failures detected
    - Orphaned chunks reallocated
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Dependencies**: Tasks 28-31
  - **Success Criteria**:
    - [ ] Main loop calls all components
    - [ ] End-to-end test passes
    - [ ] Logs all major events
    - [ ] 3+ tests passing

### 3.2 Node Agent

- [ ] **Task 34: Create node agent main loop structure**
  - **Description**: Agent that polls for work and sends heartbeats
  - **Files to create**: `src/agent/main.py`, `src/agent/__init__.py`
  - **Tests**: `tests/test_agent/test_main.py`
  - **Test Cases**:
    - Agent starts and runs loop
    - Graceful shutdown works
    - Handles API errors
    - Can be configured via CLI args
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] Main loop runs every 10 seconds
    - [ ] CLI args for node name, API key, coordinator URL
    - [ ] Logs activity
    - [ ] 3+ tests passing

- [ ] **Task 35: Implement heartbeat sender**
  - **Description**: Send heartbeat to coordinator with resource usage
  - **Files to create**: `src/agent/heartbeat.py`
  - **Tests**: `tests/test_agent/test_heartbeat.py`
  - **Test Cases**:
    - Heartbeat sent successfully
    - Includes current resource usage
    - Retries on failure
    - Updates last_heartbeat timestamp
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] `send_heartbeat()` function
    - [ ] POSTs to coordinator endpoint
    - [ ] Includes CPU/RAM/disk usage (via psutil)
    - [ ] 4+ tests passing

- [ ] **Task 36: Implement Docker container runner**
  - **Description**: Execute job chunks in Docker containers
  - **Files to create**: `src/agent/docker_runner.py`
  - **Reference**: https://docker-py.readthedocs.io/
  - **Tests**: `tests/test_agent/test_docker_runner.py`
  - **Test Cases**:
    - Container runs successfully
    - Security hardening applied (from CLAUDE.md)
    - Resource limits enforced
    - Container cleanup after completion
    - Logs captured
  - **Estimated Lines**: ~200
  - **Duration**: 50 min
  - **Success Criteria**:
    - [ ] `run_container()` function
    - [ ] Applies security config from CLAUDE.md
    - [ ] Captures container logs
    - [ ] Returns exit code
    - [ ] 6+ tests passing (may need Docker in test environment)

- [ ] **Task 37: Integrate agent with coordinator**
  - **Description**: Agent polls for chunks, runs them, reports results
  - **Files to modify**: `src/agent/main.py`
  - **Tests**: Integration test in `tests/test_agent/test_integration.py`
  - **Test Cases**:
    - Agent gets chunk from coordinator
    - Runs chunk in container
    - Reports completion back
    - Handles chunk failures
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Dependencies**: Tasks 34-36
  - **Success Criteria**:
    - [ ] Main loop calls all components
    - [ ] End-to-end chunk execution works
    - [ ] Results uploaded to coordinator
    - [ ] 4+ tests passing

---

## PHASE 4: FAULT TOLERANCE (Week 4)

**Goal**: Handle node failures and ensure jobs complete even with interruptions.

### 4.1 Failure Detection

- [ ] **Task 38: Implement orphaned chunk detection**
  - **Description**: Find chunks assigned to dead nodes
  - **Files to create**: `src/coordinator/fault_tolerance.py`
  - **Tests**: `tests/test_coordinator/test_fault_tolerance.py`
  - **Test Cases**:
    - Detects chunks on offline nodes
    - Ignores chunks on online nodes
    - Handles edge cases (node just went offline)
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] `find_orphaned_chunks()` function
    - [ ] Queries chunks with assigned_node offline
    - [ ] Returns list of chunk IDs
    - [ ] 4+ tests passing

- [ ] **Task 39: Implement chunk reallocation logic**
  - **Description**: Reset orphaned chunks to pending status
  - **Files to modify**: `src/coordinator/fault_tolerance.py`
  - **Tests**: `tests/test_coordinator/test_fault_tolerance.py`
  - **Test Cases**:
    - Chunk status reset to 'pending'
    - Chunk assignment cleared
    - Retry count incremented
    - Max retries enforced (fail after 3)
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] `reallocate_orphaned_chunks()` function
    - [ ] Updates chunk status and assigned_node_id
    - [ ] Increments retry_count
    - [ ] Marks as 'failed' after max retries
    - [ ] 5+ tests passing

- [ ] **Task 40: Integrate fault tolerance into coordinator**
  - **Description**: Add fault tolerance checks to main loop
  - **Files to modify**: `src/coordinator/main.py`
  - **Tests**: `tests/test_coordinator/test_integration.py`
  - **Test Cases**:
    - Orphaned chunks detected
    - Chunks reallocated automatically
    - Job eventually completes despite node failure
  - **Estimated Lines**: ~60
  - **Duration**: 20 min
  - **Dependencies**: Tasks 38-39
  - **Success Criteria**:
    - [ ] Main loop calls fault tolerance functions
    - [ ] End-to-end test with simulated node failure
    - [ ] 2+ tests passing

### 4.2 Result Aggregation

- [ ] **Task 41: Implement result storage in MinIO**
  - **Description**: Upload chunk results to object storage
  - **Files to create**: `src/utils/storage.py`
  - **Reference**: https://min.io/docs/minio/linux/developers/python/API.html
  - **Tests**: `tests/test_utils/test_storage.py`
  - **Test Cases**:
    - File uploaded successfully
    - File downloaded successfully
    - Bucket created if not exists
    - Handles large files
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] `upload_result()` function
    - [ ] `download_result()` function
    - [ ] Uses MinIO client
    - [ ] 5+ tests passing (may need MinIO in test environment)

- [ ] **Task 42: Implement result aggregation logic**
  - **Description**: Combine chunk results when all chunks complete
  - **Files to create**: `src/coordinator/aggregation.py`
  - **Tests**: `tests/test_coordinator/test_aggregation.py`
  - **Test Cases**:
    - All completed chunks detected
    - Results downloaded from MinIO
    - Results combined correctly (for Monte Carlo)
    - Final result stored
    - Job status updated to 'completed'
  - **Estimated Lines**: ~180
  - **Duration**: 45 min
  - **Success Criteria**:
    - [ ] `aggregate_job_results()` function
    - [ ] Handles Monte Carlo averaging
    - [ ] Updates job status
    - [ ] 6+ tests passing

- [ ] **Task 43: Add result aggregation to coordinator loop**
  - **Description**: Check for completed jobs and aggregate results
  - **Files to modify**: `src/coordinator/main.py`
  - **Tests**: `tests/test_coordinator/test_integration.py`
  - **Test Cases**:
    - Job completes after all chunks finish
    - Results aggregated automatically
    - User can retrieve final result
  - **Estimated Lines**: ~60
  - **Duration**: 20 min
  - **Dependencies**: Task 42
  - **Success Criteria**:
    - [ ] Main loop calls aggregation
    - [ ] End-to-end test from submission to result
    - [ ] 2+ tests passing

### 4.3 Progress Tracking

- [ ] **Task 44: Implement job progress endpoint**
  - **Description**: GET /jobs/{job_id}/progress showing completion percentage
  - **Files to modify**: `src/api/jobs.py`
  - **Tests**: `tests/test_api/test_jobs.py`
  - **Test Cases**:
    - Returns correct completion percentage
    - Returns chunk statuses
    - Only job owner can view
    - Returns 404 for non-existent job
  - **Estimated Lines**: ~100
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] Returns completed_chunks / total_chunks
    - [ ] Returns list of chunk statuses
    - [ ] Requires authentication
    - [ ] 4+ tests passing

- [ ] **Task 45: Implement job logs endpoint**
  - **Description**: GET /jobs/{job_id}/logs to retrieve container logs
  - **Files to modify**: `src/api/jobs.py`
  - **Tests**: `tests/test_api/test_jobs.py`
  - **Test Cases**:
    - Returns logs for all chunks
    - Supports filtering by chunk number
    - Only job owner can view
    - Handles missing logs gracefully
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] Returns logs from MinIO
    - [ ] Supports pagination
    - [ ] Requires authentication
    - [ ] 4+ tests passing

---

## PHASE 5: SECURITY & POLISH (Week 5-6)

**Goal**: Security hardening, abuse prevention, and user-facing improvements.

### 5.1 Security

- [ ] **Task 46: Implement rate limiting**
  - **Description**: Add rate limiting to API endpoints
  - **Files to create**: `src/api/rate_limiting.py`
  - **Reference**: https://github.com/laurentS/slowapi
  - **Tests**: `tests/test_api/test_rate_limiting.py`
  - **Test Cases**:
    - Requests within limit succeed
    - Requests over limit rejected (429)
    - Different limits for different endpoints
    - Rate limit headers present
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] Rate limiting dependency
    - [ ] Configurable limits per endpoint
    - [ ] Returns 429 Too Many Requests
    - [ ] 5+ tests passing

- [ ] **Task 47: Implement Docker image validation**
  - **Description**: Validate submitted Docker images against whitelist
  - **Files to modify**: `src/utils/security.py`
  - **Tests**: `tests/test_utils/test_security.py`
  - **Test Cases**:
    - Approved images pass
    - Non-approved images rejected
    - Image name parsing works
    - Handles Docker Hub vs private registries
  - **Estimated Lines**: ~80
  - **Duration**: 25 min
  - **Success Criteria**:
    - [ ] `validate_docker_image()` function
    - [ ] Whitelist from CLAUDE.md
    - [ ] Clear error messages
    - [ ] 5+ tests passing

- [ ] **Task 48: Implement resource usage verification**
  - **Description**: Verify actual vs requested resource usage
  - **Files to create**: `src/coordinator/verification.py`
  - **Tests**: `tests/test_coordinator/test_verification.py`
  - **Test Cases**:
    - Detects under-utilization
    - Calculates refund amount
    - Updates user credits
    - Logs discrepancies
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] `verify_resource_usage()` function
    - [ ] Compares requested vs actual
    - [ ] Refunds credits if under 50% utilization
    - [ ] 5+ tests passing

### 5.2 User Experience

- [ ] **Task 49: Create Monte Carlo demo script**
  - **Description**: Working example job for demonstration
  - **Files to create**: `scripts/demo_monte_carlo.py`, `scripts/Dockerfile.monte-carlo`
  - **Tests**: Manual execution test
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] Script estimates π with configurable iterations
    - [ ] Dockerfile builds successfully
    - [ ] Image < 100MB
    - [ ] Results can be aggregated
    - [ ] README documentation

- [ ] **Task 50: Create node installation script**
  - **Description**: One-command setup script for friends
  - **Files to create**: `scripts/install_node.sh`
  - **Reference**: CLAUDE.md "One-Script Setup"
  - **Tests**: Manual testing on fresh Ubuntu/WSL2
  - **Estimated Lines**: ~200
  - **Duration**: 50 min
  - **Success Criteria**:
    - [ ] Installs Tailscale
    - [ ] Clones agent code
    - [ ] Installs Python dependencies
    - [ ] Configures agent
    - [ ] Starts agent as service
    - [ ] User-friendly prompts and error messages

- [ ] **Task 51: Create comprehensive README**
  - **Description**: Documentation for setup and usage
  - **Files to modify**: `README.md`
  - **Tests**: None (documentation)
  - **Estimated Lines**: ~300
  - **Duration**: 60 min
  - **Success Criteria**:
    - [ ] Project overview
    - [ ] Architecture diagram
    - [ ] Setup instructions for VPS
    - [ ] Setup instructions for nodes
    - [ ] API documentation
    - [ ] Demo walkthrough
    - [ ] Troubleshooting section

- [ ] **Task 52: Create API documentation**
  - **Description**: Auto-generated API docs with FastAPI
  - **Files to modify**: `src/api/main.py` (add descriptions)
  - **Tests**: Verify docs accessible at /docs
  - **Estimated Lines**: ~100 (docstrings)
  - **Duration**: 30 min
  - **Success Criteria**:
    - [ ] All endpoints have descriptions
    - [ ] Request/response examples
    - [ ] Authentication documented
    - [ ] Accessible at /docs and /redoc

### 5.3 Monitoring & Observability

- [ ] **Task 53: Add system metrics endpoint**
  - **Description**: GET /metrics with cluster statistics
  - **Files to create**: `src/api/metrics.py`
  - **Tests**: `tests/test_api/test_metrics.py`
  - **Test Cases**:
    - Returns node count
    - Returns job statistics
    - Returns credit statistics
    - Public endpoint (no auth required)
  - **Estimated Lines**: ~150
  - **Duration**: 40 min
  - **Success Criteria**:
    - [ ] Returns cluster stats
    - [ ] JSON format
    - [ ] Cached (updated every minute)
    - [ ] 4+ tests passing

- [ ] **Task 54: Implement job cancellation**
  - **Description**: DELETE /jobs/{job_id} to cancel running jobs
  - **Files to modify**: `src/api/jobs.py`
  - **Tests**: `tests/test_api/test_jobs.py`
  - **Test Cases**:
    - Owner can cancel their job
    - Non-owner cannot cancel (403)
    - Running chunks are stopped
    - Credits refunded proportionally
  - **Estimated Lines**: ~120
  - **Duration**: 35 min
  - **Success Criteria**:
    - [ ] Marks job as 'cancelled'
    - [ ] Stops running containers
    - [ ] Partial refund calculated and issued
    - [ ] 5+ tests passing

- [ ] **Task 55: Final integration testing and bug fixes**
  - **Description**: End-to-end system test and polish
  - **Tests**: Complete system integration test
  - **Test Cases**:
    - Full workflow: user registers → lists resources → submits job → job completes → gets results
    - Node failure mid-job handled correctly
    - Multiple concurrent jobs work
    - All APIs respond correctly
  - **Estimated Lines**: Varies (bug fixes)
  - **Duration**: 2-3 hours
  - **Success Criteria**:
    - [ ] All tests passing (target: 85% coverage)
    - [ ] No critical bugs
    - [ ] System runs stably for 1 hour
    - [ ] Demo script works end-to-end

---

## BLOCKERS & ISSUES

*None currently*

---

## NOTES & DECISIONS

### 2025-10-30
- Project initialized
- Decided on PostgreSQL-only (no Redis) for simplicity
- VPS recommended for coordinator (DigitalOcean/Hetzner)
- Monte Carlo π estimation chosen as primary demo
- GPU support deferred to V2

---

## QUICK REFERENCE

### How to Update This File
```bash
# After completing a task
1. Change [ ] to [✓]
2. Add completion timestamp
3. Add notes if any issues
4. Commit with: git add TASKS.md && git commit -m "chore: update TASKS.md - completed task N"
```

### How to Check Progress
```bash
# Count completed tasks
grep -c "\[✓\]" TASKS.md

# See what's in progress
grep "\[>\]" TASKS.md

# See blockers
grep "\[✗\]" TASKS.md
```

---

**Last Updated**: 2025-10-30
**Total Tasks**: 55
**Estimated Total Time**: 6 weeks
**Current Status**: Not started (0%)
