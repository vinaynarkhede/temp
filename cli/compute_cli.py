#!/usr/bin/env python3
"""
Command-line interface for Compute Marketplace.

Usage:
    compute job submit --image python:3.11-slim --chunks 4
    compute job status <job-id>
    compute node register --name my-pc
    compute credits balance
"""

import click
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk.compute_marketplace_sdk import ComputeMarketplaceClient


@click.group()
@click.option('--api-key', envvar='COMPUTE_API_KEY', required=True, help='API key')
@click.option('--url', envvar='COMPUTE_URL', default='http://localhost:8000', help='API base URL')
@click.pass_context
def cli(ctx, api_key, url):
    """Compute Marketplace CLI"""
    ctx.obj = ComputeMarketplaceClient(url, api_key)


@cli.group()
def job():
    """Job management commands"""
    pass


@job.command()
@click.option('--image', required=True, help='Docker image')
@click.option('--chunks', type=int, default=4, help='Number of chunks')
@click.option('--cpu', type=int, default=2, help='CPU cores per chunk')
@click.option('--ram', type=float, default=4.0, help='RAM GB per chunk')
@click.pass_obj
def submit(client, image, chunks, cpu, ram):
    """Submit a new job"""
    job = client.submit_job(image, chunks, cpu, ram)
    click.echo(f"Job submitted: ID {job['id']}")
    click.echo(f"Status: {job['status']}")


@job.command()
@click.argument('job_id', type=int)
@click.pass_obj
def status(client, job_id):
    """Check job status"""
    job = client.get_job(job_id)
    click.echo(f"Job {job_id}:")
    click.echo(f"  Status: {job['status']}")
    click.echo(f"  Progress: {job['completed_chunks']}/{job['total_chunks']} chunks")


@job.command()
@click.pass_obj
def list(client):
    """List all jobs"""
    jobs = client.list_jobs()
    for job in jobs:
        click.echo(f"{job['id']}: {job['status']} - {job['docker_image']}")


@cli.group()
def credits():
    """Credit management commands"""
    pass


@credits.command()
@click.pass_obj
def balance(client):
    """Check credit balance"""
    balance = client.get_balance()
    click.echo(f"Credit balance: {balance}")


if __name__ == '__main__':
    cli()
