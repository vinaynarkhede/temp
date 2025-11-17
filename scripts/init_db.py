#!/usr/bin/env python3
"""
Database initialization script for Distributed Compute Marketplace.

This script:
1. Creates the database if it doesn't exist
2. Runs the schema.sql file to create tables and indexes
3. Is idempotent - safe to run multiple times

Usage:
    python scripts/init_db.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (optional)
        Format: postgresql://user:password@host:port/database
        Default: postgresql://postgres:postgres@localhost:5432/compute_marketplace
"""

import os
import sys
import logging
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_database_url(url: str) -> dict:
    """
    Parse PostgreSQL database URL into components.

    Args:
        url: Database URL in format postgresql://user:password@host:port/database

    Returns:
        Dictionary with keys: user, password, host, port, database

    Raises:
        ValueError: If URL format is invalid
    """
    if not url.startswith('postgresql://'):
        raise ValueError("DATABASE_URL must start with 'postgresql://'")

    # Remove postgresql:// prefix
    url = url.replace('postgresql://', '')

    # Split user:password@host:port/database
    try:
        if '@' in url:
            credentials, location = url.split('@')
            user, password = credentials.split(':')
        else:
            raise ValueError("Missing credentials in DATABASE_URL")

        if '/' in location:
            host_port, database = location.split('/')
        else:
            raise ValueError("Missing database name in DATABASE_URL")

        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'

        return {
            'user': user,
            'password': password,
            'host': host,
            'port': int(port),
            'database': database
        }
    except Exception as e:
        raise ValueError(f"Invalid DATABASE_URL format: {e}")


def get_database_config() -> dict:
    """
    Get database configuration from environment or use defaults.

    Returns:
        Dictionary with database connection parameters
    """
    default_url = "postgresql://postgres:postgres@localhost:5432/compute_marketplace"
    database_url = os.getenv("DATABASE_URL", default_url)

    logger.info(f"Using database URL: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    return parse_database_url(database_url)


def database_exists(config: dict) -> bool:
    """
    Check if the target database exists.

    Args:
        config: Database configuration dictionary

    Returns:
        True if database exists, False otherwise
    """
    try:
        # Connect to default 'postgres' database to check if target exists
        conn = psycopg2.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database='postgres'  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config['database'],)
        )
        exists = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return exists

    except psycopg2.Error as e:
        logger.error(f"Error checking database existence: {e}")
        raise


def create_database(config: dict):
    """
    Create the target database if it doesn't exist.

    Args:
        config: Database configuration dictionary

    Raises:
        psycopg2.Error: If database creation fails
    """
    try:
        if database_exists(config):
            logger.info(f"Database '{config['database']}' already exists")
            return

        logger.info(f"Creating database '{config['database']}'...")

        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create database
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(config['database'])
            )
        )

        cursor.close()
        conn.close()

        logger.info(f"✓ Database '{config['database']}' created successfully")

    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        raise


def run_schema(config: dict):
    """
    Run the schema.sql file to create tables and indexes.

    Args:
        config: Database configuration dictionary

    Raises:
        FileNotFoundError: If schema.sql doesn't exist
        psycopg2.Error: If schema execution fails
    """
    # Find schema.sql file
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    schema_file = project_root / 'src' / 'database' / 'schema.sql'

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    logger.info(f"Reading schema from: {schema_file}")

    # Read schema file
    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    try:
        # Connect to target database
        conn = psycopg2.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database=config['database']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        logger.info("Executing schema.sql...")

        # Execute schema
        cursor.execute(schema_sql)

        cursor.close()
        conn.close()

        logger.info("✓ Schema executed successfully")
        logger.info("✓ Tables and indexes created")

    except psycopg2.Error as e:
        logger.error(f"Error executing schema: {e}")
        raise


def verify_tables(config: dict) -> list:
    """
    Verify that all expected tables were created.

    Args:
        config: Database configuration dictionary

    Returns:
        List of table names found in database
    """
    expected_tables = [
        'users',
        'nodes',
        'resource_offers',
        'jobs',
        'job_chunks',
        'credit_transactions',
        'schema_version'
    ]

    try:
        conn = psycopg2.connect(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            database=config['database']
        )
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)

        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Check if all expected tables exist
        missing_tables = set(expected_tables) - set(tables)

        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
        else:
            logger.info(f"✓ All {len(expected_tables)} tables verified:")
            for table in expected_tables:
                logger.info(f"  - {table}")

        return tables

    except psycopg2.Error as e:
        logger.error(f"Error verifying tables: {e}")
        raise


def main():
    """
    Main function to initialize the database.

    Steps:
    1. Get database configuration
    2. Create database if needed
    3. Run schema.sql
    4. Verify tables were created

    Returns:
        0 on success, 1 on failure
    """
    try:
        logger.info("=" * 60)
        logger.info("Database Initialization Script")
        logger.info("=" * 60)

        # Get configuration
        config = get_database_config()

        # Create database
        create_database(config)

        # Run schema
        run_schema(config)

        # Verify tables
        verify_tables(config)

        logger.info("=" * 60)
        logger.info("✓ Database initialization completed successfully!")
        logger.info("=" * 60)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        logger.error("Please ensure PostgreSQL is running and credentials are correct")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
