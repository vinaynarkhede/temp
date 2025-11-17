# Distributed Compute Marketplace

A peer-to-peer compute marketplace where friends can share idle computing resources. Think "Airbnb for CPU power" among a trusted friend group.

## Overview

This project enables friends to:
- **List idle compute resources** (CPU, RAM, storage) on their machines
- **Submit containerized jobs** to run on available resources
- **Earn/spend credits** through a dual economy system (paid or donation-based)
- **Fault-tolerant execution** with automatic job chunking and reallocation

## Key Features

- **Peer-to-Peer Marketplace**: Friend-to-friend resource sharing
- **Dual Credit System**: Paid (earn/spend credits) OR donation (free, provider still earns credits)
- **Fault Tolerance**: Job chunking with automatic reallocation if nodes fail
- **Container Security**: All jobs run in hardened Docker containers with resource limits
- **Resource-Aware Scheduling**: Smart matching of job requirements to available compute

## Demo Use Case: Monte Carlo π Estimation

Demonstrates linear speedup with distributed computing:
- User submits: "Estimate π with 100M samples"
- System splits into 4 chunks of 25M each
- Runs on 4 nodes simultaneously → **4x faster**
- Aggregates results for final estimate

## Architecture

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

## Technology Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Database**: PostgreSQL
- **Storage**: MinIO (S3-compatible)
- **Containers**: Docker (via docker-py)
- **Networking**: Tailscale
- **Testing**: pytest

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- PostgreSQL (or use Docker Compose setup)
- MinIO (or use Docker Compose setup)

### Setup Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd distributed-compute-marketplace
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

7. **Start API server**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Start coordinator** (in separate terminal)
   ```bash
   python -m src.coordinator.main
   ```

9. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_api/test_auth.py -v

# Run tests matching pattern
pytest tests/ -k "test_auth" -v

# View coverage report
open htmlcov/index.html
```

## Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/ tests/

# Security audit
bandit -r src/
```

## Project Structure

```
distributed-compute-marketplace/
├── src/
│   ├── api/           # FastAPI application
│   ├── coordinator/   # Background scheduler
│   ├── agent/         # Node agent (runs on friend PCs)
│   ├── database/      # Database models and schema
│   └── utils/         # Shared utilities
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── plans/             # Task implementation plans
├── CLAUDE.md          # Development guide
└── TASKS.md           # Task tracker
```

## Development Workflow

This project follows Test-Driven Development (TDD):

1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor if needed
4. Commit only after all tests pass

See [CLAUDE.md](CLAUDE.md) for comprehensive development guidelines.

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login

### Resources
- `GET /resources/available` - Browse available compute resources
- `POST /resources/offer` - List resources for rent
- `PUT /resources/offer/{id}` - Update resource offering

### Jobs
- `POST /jobs/submit` - Submit a compute job
- `GET /jobs/{id}/progress` - Check job progress
- `GET /jobs/{id}/logs` - Retrieve job logs
- `DELETE /jobs/{id}` - Cancel running job

### Credits
- `GET /credits/balance` - Check credit balance
- `GET /credits/history` - View transaction history

### System
- `GET /health` - Health check
- `GET /metrics` - Cluster statistics

## Node Agent Installation

For friends who want to contribute compute:

```bash
curl -sSL https://your-vps-url/install_node.sh | bash
```

Or manually:
```bash
git clone <repository-url>
cd distributed-compute-marketplace
pip install -r requirements.txt
python -m src.agent.main --node-name "My-PC" --api-key "your-api-key"
```

## Database Schema

The system uses 6 PostgreSQL tables:
- `users` - User accounts and credits
- `nodes` - Friend machines offering compute
- `resource_offers` - Available compute for rent
- `jobs` - User-submitted compute jobs
- `job_chunks` - Individual tasks for fault tolerance
- `credit_transactions` - Audit trail for credit system

See [src/database/schema.sql](src/database/schema.sql) for full schema.

## Security

All jobs run in hardened Docker containers with:
- Non-root user execution
- Read-only root filesystem
- No network access
- Resource limits (CPU, RAM, PIDs)
- Dropped Linux capabilities
- Whitelisted base images only

## Contributing

1. Follow the TDD workflow
2. Maintain 85%+ test coverage
3. Use type hints everywhere
4. Keep tasks under 300 lines
5. Update TASKS.md after each task

See [CLAUDE.md](CLAUDE.md) for detailed contribution guidelines.

## Roadmap

### Phase 1: Foundation ✅ (In Progress)
- Project setup
- Authentication system
- Basic API structure

### Phase 2: Core Marketplace
- Resource listing and browsing
- Credit system
- Job submission

### Phase 3: Distribution & Scheduling
- Coordinator service
- Node agent
- Job distribution

### Phase 4: Fault Tolerance
- Failure detection
- Result aggregation
- Progress tracking

### Phase 5: Security & Polish
- Security hardening
- Monitoring & observability
- Documentation

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check [CLAUDE.md](CLAUDE.md) for development guidance
- Review [TASKS.md](TASKS.md) for task status
- Open an issue on GitHub

## Acknowledgments

Built with:
- FastAPI for the amazing async framework
- Docker for container isolation
- PostgreSQL for reliable data storage
- Tailscale for secure networking
- The Python community for excellent libraries

---

**Status**: 🚧 In Development (Phase 1)
**Target Completion**: 6 weeks
**Current Progress**: See [TASKS.md](TASKS.md)
