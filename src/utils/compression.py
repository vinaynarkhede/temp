"""
Data compression utilities for reducing storage and transfer costs.

Automatically compresses job inputs/outputs before storing in MinIO.
"""

import gzip
import zlib
import logging
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CompressionAlgorithm(Enum):
    """Supported compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"


class CompressionStats:
    """Statistics about compression operation."""
    def __init__(self, original_size: int, compressed_size: int, algorithm: str):
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.algorithm = algorithm
        self.ratio = compressed_size / original_size if original_size > 0 else 1.0
        self.savings_percent = (1 - self.ratio) * 100

    def __repr__(self):
        return (f"CompressionStats(original={self.original_size}, "
                f"compressed={self.compressed_size}, "
                f"savings={self.savings_percent:.1f}%)")


def compress_data(
    data: bytes,
    algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP,
    level: int = 6
) -> tuple[bytes, CompressionStats]:
    """
    Compress data using specified algorithm.

    Args:
        data: Raw data to compress
        algorithm: Compression algorithm to use
        level: Compression level (1-9, higher = better compression but slower)

    Returns:
        Tuple of (compressed_data, stats)
    """
    original_size = len(data)

    if algorithm == CompressionAlgorithm.GZIP:
        compressed = gzip.compress(data, compresslevel=level)
    elif algorithm == CompressionAlgorithm.ZLIB:
        compressed = zlib.compress(data, level=level)
    else:
        # No compression
        compressed = data

    stats = CompressionStats(
        original_size=original_size,
        compressed_size=len(compressed),
        algorithm=algorithm.value
    )

    logger.info(f"Compressed data: {stats}")
    return compressed, stats


def decompress_data(
    data: bytes,
    algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP
) -> bytes:
    """
    Decompress data.

    Args:
        data: Compressed data
        algorithm: Algorithm used for compression

    Returns:
        Decompressed data
    """
    if algorithm == CompressionAlgorithm.GZIP:
        return gzip.decompress(data)
    elif algorithm == CompressionAlgorithm.ZLIB:
        return zlib.decompress(data)
    else:
        return data


def should_compress(data_size: int, threshold_bytes: int = 1024) -> bool:
    """
    Determine if data should be compressed.

    Small data may not benefit from compression (overhead > savings).

    Args:
        data_size: Size of data in bytes
        threshold_bytes: Minimum size to compress (default 1KB)

    Returns:
        True if data should be compressed
    """
    return data_size >= threshold_bytes


def auto_compress(data: bytes, threshold_bytes: int = 1024) -> tuple[bytes, str]:
    """
    Automatically compress data if beneficial.

    Args:
        data: Raw data
        threshold_bytes: Minimum size to attempt compression

    Returns:
        Tuple of (data, algorithm_used)
        If compression not beneficial, returns original data
    """
    if not should_compress(len(data), threshold_bytes):
        return data, CompressionAlgorithm.NONE.value

    compressed, stats = compress_data(data, CompressionAlgorithm.GZIP)

    # Only use compression if we save at least 10%
    if stats.savings_percent >= 10:
        logger.info(f"Compression beneficial: {stats}")
        return compressed, CompressionAlgorithm.GZIP.value
    else:
        logger.info(f"Compression not beneficial: {stats}, using original")
        return data, CompressionAlgorithm.NONE.value


def estimate_compressed_size(original_size: int, compression_ratio: float = 0.3) -> int:
    """
    Estimate compressed size based on typical ratio.

    Args:
        original_size: Original data size in bytes
        compression_ratio: Expected compression ratio (default 0.3 = 70% reduction)

    Returns:
        Estimated compressed size
    """
    return int(original_size * compression_ratio)
