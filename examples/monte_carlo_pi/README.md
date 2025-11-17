# Monte Carlo Pi Estimation Example

Demonstrates distributed computing with a parallelizable workload.

## How it Works

1. Job is split into 4 chunks (25M samples each = 100M total)
2. Each chunk runs independently on different nodes
3. Results are aggregated: `π ≈ average(all_chunk_results)`
4. Shows linear speedup with more nodes

## Build and Test Locally

```bash
docker build -t monte-carlo-pi .
docker run monte-carlo-pi
```

## Submit to Marketplace

```python
from sdk.compute_marketplace_sdk import ComputeMarketplaceClient

client = ComputeMarketplaceClient("http://localhost:8000", "your-api-key")

job = client.submit_job(
    docker_image="monte-carlo-pi:latest",
    total_chunks=4,
    cpu_cores_per_chunk=2,
    ram_gb_per_chunk=4.0,
    estimated_duration_hours=0.5
)

print(f"Job ID: {job['id']}")
```

## Expected Results

- Single chunk (25M samples): π ≈ 3.1415... (±0.0001)
- 4 chunks aggregated: π ≈ 3.14159... (±0.00001)
- Speedup: ~4x faster with 4 nodes
