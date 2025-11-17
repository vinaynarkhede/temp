"""
MinIO storage utilities for job results and data.

Handles uploading and downloading of job inputs/outputs.
"""

import logging
import io
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
import os

logger = logging.getLogger(__name__)


# MinIO configuration from environment
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Default bucket for job results
RESULTS_BUCKET = "job-results"
INPUTS_BUCKET = "job-inputs"


def get_minio_client() -> Minio:
    """
    Get MinIO client instance.

    Returns:
        Configured MinIO client
    """
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )


def ensure_bucket_exists(client: Minio, bucket_name: str) -> None:
    """
    Ensure a bucket exists, create if it doesn't.

    Args:
        client: MinIO client
        bucket_name: Name of bucket to check/create
    """
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"Created MinIO bucket: {bucket_name}")
    except S3Error as e:
        logger.error(f"Error ensuring bucket exists: {e}")
        raise


def upload_result(job_id: int, chunk_number: int, data: bytes) -> str:
    """
    Upload job chunk result to MinIO.

    Args:
        job_id: Job ID
        chunk_number: Chunk number
        data: Result data as bytes

    Returns:
        Object key/path in MinIO

    Raises:
        S3Error: If upload fails
    """
    client = get_minio_client()
    ensure_bucket_exists(client, RESULTS_BUCKET)

    object_name = f"job_{job_id}/chunk_{chunk_number}/result.bin"

    try:
        client.put_object(
            RESULTS_BUCKET,
            object_name,
            io.BytesIO(data),
            length=len(data)
        )
        logger.info(f"Uploaded result for job {job_id} chunk {chunk_number}")
        return object_name
    except S3Error as e:
        logger.error(f"Failed to upload result: {e}")
        raise


def download_result(job_id: int, chunk_number: int) -> bytes:
    """
    Download job chunk result from MinIO.

    Args:
        job_id: Job ID
        chunk_number: Chunk number

    Returns:
        Result data as bytes

    Raises:
        S3Error: If download fails or object not found
    """
    client = get_minio_client()
    object_name = f"job_{job_id}/chunk_{chunk_number}/result.bin"

    try:
        response = client.get_object(RESULTS_BUCKET, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        logger.info(f"Downloaded result for job {job_id} chunk {chunk_number}")
        return data
    except S3Error as e:
        logger.error(f"Failed to download result: {e}")
        raise


def upload_job_input(job_id: int, data: bytes) -> str:
    """
    Upload job input data to MinIO.

    Args:
        job_id: Job ID
        data: Input data as bytes

    Returns:
        Object key/path in MinIO
    """
    client = get_minio_client()
    ensure_bucket_exists(client, INPUTS_BUCKET)

    object_name = f"job_{job_id}/input.bin"

    try:
        client.put_object(
            INPUTS_BUCKET,
            object_name,
            io.BytesIO(data),
            length=len(data)
        )
        logger.info(f"Uploaded input for job {job_id}")
        return object_name
    except S3Error as e:
        logger.error(f"Failed to upload input: {e}")
        raise


def download_job_input(job_id: int) -> bytes:
    """
    Download job input data from MinIO.

    Args:
        job_id: Job ID

    Returns:
        Input data as bytes
    """
    client = get_minio_client()
    object_name = f"job_{job_id}/input.bin"

    try:
        response = client.get_object(INPUTS_BUCKET, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    except S3Error as e:
        logger.error(f"Failed to download input: {e}")
        raise


def list_job_results(job_id: int) -> list:
    """
    List all result objects for a job.

    Args:
        job_id: Job ID

    Returns:
        List of object names
    """
    client = get_minio_client()
    prefix = f"job_{job_id}/"

    try:
        objects = client.list_objects(RESULTS_BUCKET, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]
    except S3Error as e:
        logger.error(f"Failed to list results: {e}")
        return []


def delete_job_data(job_id: int) -> None:
    """
    Delete all data for a job (inputs and results).

    Args:
        job_id: Job ID
    """
    client = get_minio_client()

    # Delete from results bucket
    try:
        objects = list_job_results(job_id)
        for obj in objects:
            client.remove_object(RESULTS_BUCKET, obj)
        logger.info(f"Deleted result data for job {job_id}")
    except S3Error as e:
        logger.error(f"Failed to delete results: {e}")

    # Delete from inputs bucket
    try:
        input_obj = f"job_{job_id}/input.bin"
        client.remove_object(INPUTS_BUCKET, input_obj)
        logger.info(f"Deleted input data for job {job_id}")
    except S3Error as e:
        logger.error(f"Failed to delete input: {e}")
