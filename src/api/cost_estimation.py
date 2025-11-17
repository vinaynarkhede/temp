"""Cost estimation endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel
from src.utils.credits import calculate_chunk_cost

router = APIRouter()


class JobCostEstimate(BaseModel):
    """Job parameters for cost estimation."""
    cpu_cores_per_chunk: int
    ram_gb_per_chunk: float
    total_chunks: int
    estimated_duration_hours: float = 1.0


class CostEstimateResponse(BaseModel):
    """Cost estimation response."""
    total_credits: int
    credits_per_chunk: int
    estimated_completion_minutes: float
    estimated_nodes_needed: int


@router.post("/estimate", response_model=CostEstimateResponse)
async def estimate_job_cost(estimate: JobCostEstimate):
    """
    Estimate cost before submitting a job.

    Helps users understand pricing before committing credits.
    """
    total_cost = calculate_chunk_cost(
        cpu_cores_per_chunk=estimate.cpu_cores_per_chunk,
        ram_gb_per_chunk=estimate.ram_gb_per_chunk,
        total_chunks=estimate.total_chunks,
        estimated_duration_hours=estimate.estimated_duration_hours
    )

    cost_per_chunk = total_cost // estimate.total_chunks

    # Estimate completion time (assumes perfect parallelization)
    completion_minutes = estimate.estimated_duration_hours * 60

    return CostEstimateResponse(
        total_credits=total_cost,
        credits_per_chunk=cost_per_chunk,
        estimated_completion_minutes=completion_minutes,
        estimated_nodes_needed=estimate.total_chunks
    )


@router.get("/templates/{template_name}/estimate")
async def estimate_template_cost(template_name: str):
    """Get cost estimate for a job template."""
    from src.api.templates import get_template

    template = get_template(template_name)
    if not template:
        from fastapi import HTTPException
        raise HTTPException(404, "Template not found")

    total_cost = calculate_chunk_cost(
        cpu_cores_per_chunk=template["cpu_cores_per_chunk"],
        ram_gb_per_chunk=template["ram_gb_per_chunk"],
        total_chunks=template["total_chunks"],
        estimated_duration_hours=template["estimated_duration_hours"]
    )

    return {
        "template_name": template_name,
        "total_credits": total_cost,
        "estimated_hours": template["estimated_duration_hours"]
    }
