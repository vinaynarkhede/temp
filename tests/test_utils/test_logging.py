"""
Tests for logging configuration.

Following TDD: These tests are written BEFORE implementation.
"""

import pytest
import logging
import os
from pathlib import Path


class TestLoggingConfiguration:
    """Test suite for logging configuration."""

    def test_setup_logging_creates_logger(self):
        """Test that setup_logging() returns a configured logger."""
        from src.utils.logging_config import setup_logging

        logger = setup_logging("test_module")

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_setup_logging_sets_correct_level_development(self, monkeypatch):
        """Test that logging level is DEBUG in development mode."""
        from src.utils.logging_config import setup_logging

        monkeypatch.setenv("ENVIRONMENT", "development")
        logger = setup_logging("test_module")

        assert logger.level == logging.DEBUG

    def test_setup_logging_sets_correct_level_production(self, monkeypatch):
        """Test that logging level is INFO in production mode."""
        from src.utils.logging_config import setup_logging

        monkeypatch.setenv("ENVIRONMENT", "production")
        logger = setup_logging("test_module")

        assert logger.level == logging.INFO

    def test_setup_logging_creates_logs_directory(self, tmp_path, monkeypatch):
        """Test that logs directory is created if it doesn't exist."""
        from src.utils.logging_config import setup_logging

        # Use temporary directory for testing
        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        assert not log_dir.exists()

        setup_logging("test_module")

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_setup_logging_creates_file_handler(self, tmp_path, monkeypatch):
        """Test that file handler is added to logger."""
        from src.utils.logging_config import setup_logging

        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        logger = setup_logging("test_module")

        # Check that at least one file handler exists
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_setup_logging_creates_console_handler(self):
        """Test that console handler is added to logger."""
        from src.utils.logging_config import setup_logging

        logger = setup_logging("test_module")

        # Check that at least one stream handler exists (console)
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) > 0

    def test_setup_logging_formats_messages_correctly(self, tmp_path, monkeypatch):
        """Test that log messages are formatted correctly."""
        from src.utils.logging_config import setup_logging

        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        logger = setup_logging("test_format_check")

        # Check that handlers have formatters configured
        assert len(logger.handlers) > 0

        for handler in logger.handlers:
            formatter = handler.formatter
            assert formatter is not None
            # Check format string contains expected fields
            assert "%(asctime)s" in formatter._fmt or "asctime" in str(formatter._fmt)
            assert "%(name)s" in formatter._fmt or "name" in str(formatter._fmt)
            assert "%(levelname)s" in formatter._fmt or "levelname" in str(formatter._fmt)
            assert "%(message)s" in formatter._fmt or "message" in str(formatter._fmt)

    def test_setup_logging_writes_to_file(self, tmp_path, monkeypatch):
        """Test that log messages are written to file."""
        from src.utils.logging_config import setup_logging

        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        logger = setup_logging("test_file_write")
        logger.info("Test file write")

        # Flush all handlers to ensure data is written
        for handler in logger.handlers:
            handler.flush()

        # Find log file
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0

        # Read log file and verify message
        log_content = log_files[0].read_text()
        assert "Test file write" in log_content
        assert "INFO" in log_content

    def test_setup_logging_handles_rotating_files(self, tmp_path, monkeypatch):
        """Test that file rotation is configured."""
        from src.utils.logging_config import setup_logging

        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        logger = setup_logging("test_module")

        # Check if RotatingFileHandler is used
        from logging.handlers import RotatingFileHandler
        rotating_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]

        # Should have at least one rotating file handler
        assert len(rotating_handlers) > 0

    def test_get_logger_returns_configured_logger(self):
        """Test that get_logger() returns a properly configured logger."""
        from src.utils.logging_config import get_logger

        logger = get_logger(__name__)

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logger_hierarchy_works(self):
        """Test that logger hierarchy is maintained."""
        from src.utils.logging_config import get_logger

        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")

        assert child_logger.parent == parent_logger or child_logger.name.startswith(parent_logger.name)

    def test_setup_logging_is_idempotent(self, tmp_path, monkeypatch):
        """Test that calling setup_logging multiple times doesn't duplicate handlers."""
        from src.utils.logging_config import setup_logging

        log_dir = tmp_path / "logs"
        monkeypatch.setenv("LOG_DIR", str(log_dir))

        logger1 = setup_logging("test_module")
        initial_handler_count = len(logger1.handlers)

        logger2 = setup_logging("test_module")

        # Should not have duplicate handlers
        assert len(logger2.handlers) == initial_handler_count
