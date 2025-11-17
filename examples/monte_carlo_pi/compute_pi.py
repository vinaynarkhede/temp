#!/usr/bin/env python3
"""
Monte Carlo Pi Estimation - Example job for distributed compute.

Estimates π by randomly sampling points in a unit square.
"""

import random
import sys


def estimate_pi(num_samples: int) -> float:
    """
    Estimate π using Monte Carlo method.

    Args:
        num_samples: Number of random points to sample

    Returns:
        Estimated value of π
    """
    inside_circle = 0

    for _ in range(num_samples):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)

        # Check if point is inside quarter circle
        if x**2 + y**2 <= 1:
            inside_circle += 1

    # π/4 = inside_circle / total_points
    pi_estimate = 4 * inside_circle / num_samples
    return pi_estimate


if __name__ == "__main__":
    # Get number of samples from command line or use default
    samples = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000

    print(f"Estimating π with {samples:,} samples...")
    result = estimate_pi(samples)
    print(f"π ≈ {result}")
    print(f"Error: {abs(result - 3.14159265359):.10f}")
