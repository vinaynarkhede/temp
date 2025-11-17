-- Distributed Compute Marketplace Database Schema
-- PostgreSQL 15+
--
-- This schema defines the 6 core tables for the peer-to-peer compute marketplace:
-- 1. users - User accounts and authentication
-- 2. nodes - Friend machines offering compute resources
-- 3. resource_offers - Available compute for rent
-- 4. jobs - User-submitted compute jobs
-- 5. job_chunks - Individual tasks for fault tolerance
-- 6. credit_transactions - Audit trail for credit system

-- Drop tables in reverse dependency order (for clean re-initialization)
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS job_chunks CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS resource_offers CASCADE;
DROP TABLE IF EXISTS nodes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- TABLE: users
-- ============================================================================
-- User accounts with authentication and credit balance
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    credit_balance INT DEFAULT 100 NOT NULL CHECK (credit_balance >= 0),
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================================================
-- TABLE: nodes
-- ============================================================================
-- Friend machines that offer computing resources
CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    tailscale_ip VARCHAR(45) NOT NULL,
    cpu_cores INT NOT NULL CHECK (cpu_cores > 0),
    ram_gb FLOAT NOT NULL CHECK (ram_gb > 0),
    storage_gb FLOAT NOT NULL CHECK (storage_gb > 0),
    status VARCHAR(20) DEFAULT 'offline' NOT NULL
        CHECK (status IN ('online', 'offline', 'maintenance')),
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,

    -- Each user can have multiple nodes, but each node has unique name per owner
    UNIQUE(owner_id, name)
);

-- ============================================================================
-- TABLE: resource_offers
-- ============================================================================
-- Available compute resources for rent
CREATE TABLE resource_offers (
    id SERIAL PRIMARY KEY,
    node_id INT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    cpu_cores_available INT NOT NULL CHECK (cpu_cores_available >= 0),
    ram_gb_available FLOAT NOT NULL CHECK (ram_gb_available >= 0),
    storage_gb_available FLOAT NOT NULL CHECK (storage_gb_available >= 0),
    offer_type VARCHAR(20) NOT NULL CHECK (offer_type IN ('paid', 'free')),
    approval_policy VARCHAR(20) DEFAULT 'manual' NOT NULL
        CHECK (approval_policy IN ('auto_all', 'auto_friends', 'manual')),
    trusted_users INT[] DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================================================
-- TABLE: jobs
-- ============================================================================
-- User-submitted compute jobs
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    docker_image VARCHAR(255) NOT NULL,
    total_chunks INT NOT NULL CHECK (total_chunks > 0),
    completed_chunks INT DEFAULT 0 NOT NULL CHECK (completed_chunks >= 0),
    status VARCHAR(20) DEFAULT 'pending' NOT NULL
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    priority INT DEFAULT 5 NOT NULL CHECK (priority BETWEEN 1 AND 10),
    cpu_cores_per_chunk INT NOT NULL CHECK (cpu_cores_per_chunk > 0),
    ram_gb_per_chunk FLOAT NOT NULL CHECK (ram_gb_per_chunk > 0),
    estimated_duration_hours FLOAT CHECK (estimated_duration_hours > 0),
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP,

    -- Constraint: completed_chunks cannot exceed total_chunks
    CONSTRAINT completed_le_total CHECK (completed_chunks <= total_chunks)
);

-- ============================================================================
-- TABLE: job_chunks
-- ============================================================================
-- Individual task chunks for distributed execution and fault tolerance
CREATE TABLE job_chunks (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    chunk_number INT NOT NULL CHECK (chunk_number >= 0),
    assigned_node_id INT REFERENCES nodes(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL
        CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input_data TEXT,
    output_data TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    retry_count INT DEFAULT 0 NOT NULL CHECK (retry_count >= 0),

    -- Each chunk number must be unique within a job
    UNIQUE(job_id, chunk_number)
);

-- ============================================================================
-- TABLE: credit_transactions
-- ============================================================================
-- Audit trail for all credit transfers
CREATE TABLE credit_transactions (
    id SERIAL PRIMARY KEY,
    from_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    to_user_id INT REFERENCES users(id) ON DELETE SET NULL,
    amount INT NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(50) NOT NULL
        CHECK (transaction_type IN ('job_payment', 'donation_reward', 'initial_credits', 'refund')),
    job_id INT REFERENCES jobs(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users table indexes
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Nodes table indexes
CREATE INDEX idx_nodes_owner ON nodes(owner_id);
CREATE INDEX idx_nodes_status ON nodes(status);
CREATE INDEX idx_nodes_last_heartbeat ON nodes(last_heartbeat);

-- Resource offers table indexes
CREATE INDEX idx_resource_offers_node ON resource_offers(node_id);
CREATE INDEX idx_resource_offers_active ON resource_offers(active);
CREATE INDEX idx_resource_offers_offer_type ON resource_offers(offer_type);

-- Jobs table indexes
CREATE INDEX idx_jobs_owner ON jobs(owner_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_priority ON jobs(priority);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_status_priority ON jobs(status, priority); -- Composite for scheduler

-- Job chunks table indexes
CREATE INDEX idx_job_chunks_job ON job_chunks(job_id);
CREATE INDEX idx_job_chunks_status ON job_chunks(status);
CREATE INDEX idx_job_chunks_assigned_node ON job_chunks(assigned_node_id);
CREATE INDEX idx_job_chunks_job_status ON job_chunks(job_id, status); -- Composite for aggregation

-- Credit transactions table indexes
CREATE INDEX idx_credit_transactions_from_user ON credit_transactions(from_user_id);
CREATE INDEX idx_credit_transactions_to_user ON credit_transactions(to_user_id);
CREATE INDEX idx_credit_transactions_job ON credit_transactions(job_id);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for resource_offers table
CREATE TRIGGER update_resource_offers_updated_at
    BEFORE UPDATE ON resource_offers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts with authentication credentials and credit balance';
COMMENT ON TABLE nodes IS 'Physical/virtual machines offering compute resources';
COMMENT ON TABLE resource_offers IS 'Active listings of available compute resources';
COMMENT ON TABLE jobs IS 'User-submitted distributed compute jobs';
COMMENT ON TABLE job_chunks IS 'Individual execution units for distributed jobs (fault tolerance)';
COMMENT ON TABLE credit_transactions IS 'Immutable audit log of all credit transfers';

COMMENT ON COLUMN users.api_key IS 'Unique API key for authentication (generated with secrets.token_urlsafe)';
COMMENT ON COLUMN nodes.tailscale_ip IS 'Tailscale VPN IP address for secure node communication';
COMMENT ON COLUMN resource_offers.approval_policy IS 'auto_all: approve all, auto_friends: trusted_users only, manual: require approval';
COMMENT ON COLUMN resource_offers.trusted_users IS 'Array of user IDs allowed to use this resource (for auto_friends policy)';
COMMENT ON COLUMN jobs.priority IS '1=highest, 10=lowest priority for scheduling';
COMMENT ON COLUMN job_chunks.retry_count IS 'Number of times this chunk has been retried after failure';

-- ============================================================================
-- INITIAL DATA (Optional - for development/testing)
-- ============================================================================

-- This section can be used to insert seed data for testing
-- Uncomment if needed for development environment

-- INSERT INTO users (username, email, password_hash, api_key, credit_balance) VALUES
-- ('admin', 'admin@example.com', '$2b$12$placeholder_hash', 'dev_api_key_admin_123', 1000);

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

-- Track schema version for migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT NOW() NOT NULL,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
(1, 'Initial schema with 6 core tables: users, nodes, resource_offers, jobs, job_chunks, credit_transactions');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
