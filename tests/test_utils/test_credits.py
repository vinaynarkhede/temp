"""
Tests for credit calculation utility.

Following TDD: These tests verify the credit calculation logic.
"""

import pytest


class TestCreditCalculation:
    """Test suite for credit cost calculation."""

    def test_calculate_job_cost_basic(self):
        """Test basic credit calculation for a job."""
        from src.utils.credits import calculate_job_cost

        # 4 CPU cores, 8GB RAM, 1 hour
        # Cost = (4 * 10 + 8 * 2) * 1 = 56 credits
        cost = calculate_job_cost(cpu_cores=4, ram_gb=8.0, estimated_duration_hours=1.0)

        assert cost == 56

    def test_calculate_job_cost_fractional_hours(self):
        """Test credit calculation with fractional hours."""
        from src.utils.credits import calculate_job_cost

        # 2 CPU cores, 4GB RAM, 0.5 hours
        # Cost = (2 * 10 + 4 * 2) * 0.5 = 14 credits
        cost = calculate_job_cost(cpu_cores=2, ram_gb=4.0, estimated_duration_hours=0.5)

        assert cost == 14

    def test_calculate_job_cost_multiple_hours(self):
        """Test credit calculation for multi-hour jobs."""
        from src.utils.credits import calculate_job_cost

        # 8 CPU cores, 16GB RAM, 3 hours
        # Cost = (8 * 10 + 16 * 2) * 3 = 336 credits
        cost = calculate_job_cost(cpu_cores=8, ram_gb=16.0, estimated_duration_hours=3.0)

        assert cost == 336

    def test_calculate_job_cost_defaults_to_one_hour(self):
        """Test that duration defaults to 1 hour if not specified."""
        from src.utils.credits import calculate_job_cost

        # 4 CPU cores, 8GB RAM (no duration specified)
        cost = calculate_job_cost(cpu_cores=4, ram_gb=8.0)

        assert cost == 56  # Same as 1 hour

    def test_calculate_job_cost_minimal_resources(self):
        """Test calculation with minimal resources."""
        from src.utils.credits import calculate_job_cost

        # 1 CPU core, 0.5GB RAM, 1 hour
        # Cost = (1 * 10 + 0.5 * 2) * 1 = 11 credits
        cost = calculate_job_cost(cpu_cores=1, ram_gb=0.5, estimated_duration_hours=1.0)

        assert cost == 11

    def test_calculate_job_cost_large_resources(self):
        """Test calculation with large resource requirements."""
        from src.utils.credits import calculate_job_cost

        # 32 CPU cores, 128GB RAM, 10 hours
        # Cost = (32 * 10 + 128 * 2) * 10 = 5760 credits
        cost = calculate_job_cost(cpu_cores=32, ram_gb=128.0, estimated_duration_hours=10.0)

        assert cost == 5760

    @pytest.mark.parametrize("cpu_cores,ram_gb,duration,expected", [
        (1, 1.0, 1.0, 12),      # (1*10 + 1*2) * 1 = 12
        (2, 2.0, 1.0, 24),      # (2*10 + 2*2) * 1 = 24
        (4, 8.0, 2.0, 112),     # (4*10 + 8*2) * 2 = 112
        (8, 16.0, 0.25, 28),    # (8*10 + 16*2) * 0.25 = 28
        (16, 32.0, 4.0, 896),   # (16*10 + 32*2) * 4 = 896
    ])
    def test_calculate_job_cost_parametrized(self, cpu_cores, ram_gb, duration, expected):
        """Test credit calculation with various parameter combinations."""
        from src.utils.credits import calculate_job_cost

        cost = calculate_job_cost(cpu_cores=cpu_cores, ram_gb=ram_gb, estimated_duration_hours=duration)

        assert cost == expected

    def test_calculate_job_cost_returns_integer(self):
        """Test that cost is always returned as an integer."""
        from src.utils.credits import calculate_job_cost

        # Test with values that might produce float
        cost = calculate_job_cost(cpu_cores=3, ram_gb=7.5, estimated_duration_hours=1.5)

        assert isinstance(cost, int)
        assert cost == 67  # (3*10 + 7.5*2) * 1.5 = 67.5 -> 67

    def test_calculate_job_cost_zero_duration(self):
        """Test that zero duration results in zero cost."""
        from src.utils.credits import calculate_job_cost

        cost = calculate_job_cost(cpu_cores=4, ram_gb=8.0, estimated_duration_hours=0.0)

        assert cost == 0

    def test_calculate_job_cost_validation_negative_cpu(self):
        """Test that negative CPU cores raises ValueError."""
        from src.utils.credits import calculate_job_cost

        with pytest.raises(ValueError, match="CPU cores must be positive"):
            calculate_job_cost(cpu_cores=-1, ram_gb=8.0, estimated_duration_hours=1.0)

    def test_calculate_job_cost_validation_negative_ram(self):
        """Test that negative RAM raises ValueError."""
        from src.utils.credits import calculate_job_cost

        with pytest.raises(ValueError, match="RAM must be positive"):
            calculate_job_cost(cpu_cores=4, ram_gb=-8.0, estimated_duration_hours=1.0)

    def test_calculate_job_cost_validation_negative_duration(self):
        """Test that negative duration raises ValueError."""
        from src.utils.credits import calculate_job_cost

        with pytest.raises(ValueError, match="Duration must be non-negative"):
            calculate_job_cost(cpu_cores=4, ram_gb=8.0, estimated_duration_hours=-1.0)


class TestCalculateChunkCost:
    """Test suite for chunked job cost calculation."""

    def test_calculate_chunk_cost_single_chunk(self):
        """Test cost calculation for single chunk."""
        from src.utils.credits import calculate_chunk_cost

        # 4 cores, 8GB RAM, 1 chunk, 1 hour
        # Cost = (4*10 + 8*2) * 1 * 1 = 56
        cost = calculate_chunk_cost(
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0,
            total_chunks=1,
            estimated_duration_hours=1.0
        )

        assert cost == 56

    def test_calculate_chunk_cost_multiple_chunks(self):
        """Test cost calculation for multiple chunks."""
        from src.utils.credits import calculate_chunk_cost

        # 2 cores, 4GB RAM, 4 chunks, 1 hour
        # Cost per chunk = (2*10 + 4*2) * 1 = 28
        # Total = 28 * 4 = 112
        cost = calculate_chunk_cost(
            cpu_cores_per_chunk=2,
            ram_gb_per_chunk=4.0,
            total_chunks=4,
            estimated_duration_hours=1.0
        )

        assert cost == 112

    def test_calculate_chunk_cost_with_duration(self):
        """Test chunked cost with custom duration."""
        from src.utils.credits import calculate_chunk_cost

        # 4 cores, 8GB RAM, 2 chunks, 2 hours
        # Cost per chunk = (4*10 + 8*2) * 2 = 112
        # Total = 112 * 2 = 224
        cost = calculate_chunk_cost(
            cpu_cores_per_chunk=4,
            ram_gb_per_chunk=8.0,
            total_chunks=2,
            estimated_duration_hours=2.0
        )

        assert cost == 224


class TestCreditWeights:
    """Test suite for credit weight constants."""

    def test_credit_weights_exist(self):
        """Test that credit weight constants are defined."""
        from src.utils.credits import CREDIT_WEIGHTS

        assert 'cpu_core_per_hour' in CREDIT_WEIGHTS
        assert 'ram_gb_per_hour' in CREDIT_WEIGHTS

    def test_credit_weights_values(self):
        """Test that credit weights have expected values."""
        from src.utils.credits import CREDIT_WEIGHTS

        assert CREDIT_WEIGHTS['cpu_core_per_hour'] == 10
        assert CREDIT_WEIGHTS['ram_gb_per_hour'] == 2
