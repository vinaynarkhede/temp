"""Job templates for common use cases."""

JOB_TEMPLATES = {
    "monte_carlo_pi": {
        "name": "Monte Carlo Pi Estimation",
        "description": "Estimate π using Monte Carlo method",
        "docker_image": "python:3.11-slim",
        "total_chunks": 4,
        "cpu_cores_per_chunk": 2,
        "ram_gb_per_chunk": 4.0,
        "estimated_duration_hours": 1.0,
        "priority": 5
    },
    "data_processing": {
        "name": "Data Processing",
        "description": "Process large datasets in parallel",
        "docker_image": "python:3.11-slim",
        "total_chunks": 8,
        "cpu_cores_per_chunk": 2,
        "ram_gb_per_chunk": 8.0,
        "estimated_duration_hours": 2.0,
        "priority": 5
    },
    "ml_training": {
        "name": "ML Model Training",
        "description": "Train machine learning models",
        "docker_image": "python:3.11-slim",
        "total_chunks": 2,
        "cpu_cores_per_chunk": 4,
        "ram_gb_per_chunk": 16.0,
        "estimated_duration_hours": 4.0,
        "priority": 7
    }
}


def get_template(template_name: str) -> dict:
    """Get job template by name."""
    return JOB_TEMPLATES.get(template_name)


def list_templates() -> list:
    """List all available templates."""
    return [
        {"id": key, **value}
        for key, value in JOB_TEMPLATES.items()
    ]
