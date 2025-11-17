"""
Tests for coordinator main service.

Following TDD: These tests verify the coordinator loop logic.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestCoordinatorMain:
    """Test suite for coordinator main loop."""

    @patch('src.coordinator.main.schedule_pending_jobs')
    @patch('src.coordinator.main.get_session')
    def test_coordinator_imports_successfully(self, mock_get_session, mock_schedule):
        """Test that coordinator module can be imported."""
        from src.coordinator import main

        assert hasattr(main, 'run_coordinator')
        assert callable(main.run_coordinator)

    @patch('src.coordinator.main.schedule_pending_jobs')
    @patch('src.coordinator.main.get_session')
    @patch('time.sleep', side_effect=KeyboardInterrupt)  # Stop after first iteration
    def test_coordinator_runs_scheduler(self, mock_sleep, mock_get_session, mock_schedule):
        """Test that coordinator calls scheduler in loop."""
        from src.coordinator.main import run_coordinator

        # Setup mock session
        mock_session = MagicMock()
        mock_get_session.return_value = MagicMock(return_value=mock_session)
        mock_schedule.return_value = 0

        # Run coordinator (will stop after one iteration due to KeyboardInterrupt)
        try:
            run_coordinator(interval_seconds=1)
        except KeyboardInterrupt:
            pass

        # Verify scheduler was called
        mock_schedule.assert_called_once()
        mock_session.close.assert_called()

    @patch('src.coordinator.main.schedule_pending_jobs')
    @patch('src.coordinator.main.get_session')
    @patch('time.sleep', side_effect=KeyboardInterrupt)
    def test_coordinator_closes_session_after_iteration(self, mock_sleep, mock_get_session, mock_schedule):
        """Test that coordinator properly closes database session."""
        from src.coordinator.main import run_coordinator

        mock_session = MagicMock()
        mock_get_session.return_value = MagicMock(return_value=mock_session)
        mock_schedule.return_value = 2

        try:
            run_coordinator(interval_seconds=1)
        except KeyboardInterrupt:
            pass

        # Verify session was closed
        mock_session.close.assert_called_once()
