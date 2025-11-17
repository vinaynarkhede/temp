"""
Multi-level job sandboxing for security vs performance trade-offs.

Users can choose security level based on trust and requirements.
"""

import logging
from enum import Enum
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SandboxLevel(Enum):
    """Security sandbox levels."""
    TRUSTED = "trusted"       # Friend's code, minimal restrictions (fastest)
    STANDARD = "standard"     # Default Docker hardening (balanced)
    PARANOID = "paranoid"     # Maximum isolation (slowest, most secure)


class SandboxConfig:
    """Container security configuration for each sandbox level."""

    # Base config (applies to all levels)
    BASE_CONFIG = {
        "user": "1000:1000",  # Non-root user
        "read_only": True,    # Read-only root filesystem
    }

    # Level-specific configurations
    CONFIGS = {
        SandboxLevel.TRUSTED: {
            # Minimal restrictions for trusted code
            "security_opt": [],
            "cap_drop": [],
            "network_mode": "bridge",  # Network access allowed
            "pids_limit": 1000,
            "ulimits": [],
            "privileged": False,
            "description": "Minimal security for trusted friend code. Fast execution.",
            "performance_penalty": "0%"
        },
        SandboxLevel.STANDARD: {
            # Standard Docker hardening (default)
            "security_opt": ["no-new-privileges"],
            "cap_drop": ["ALL"],
            "network_mode": "none",  # No network
            "pids_limit": 100,
            "ulimits": [
                {"name": "nofile", "soft": 1024, "hard": 2048},
                {"name": "nproc", "soft": 50, "hard": 100}
            ],
            "privileged": False,
            "description": "Standard security hardening. Good balance.",
            "performance_penalty": "~5%"
        },
        SandboxLevel.PARANOID: {
            # Maximum isolation
            "security_opt": [
                "no-new-privileges",
                "apparmor=docker-default",
                "seccomp=default"
            ],
            "cap_drop": ["ALL"],
            "network_mode": "none",
            "pids_limit": 50,
            "ulimits": [
                {"name": "nofile", "soft": 512, "hard": 1024},
                {"name": "nproc", "soft": 25, "hard": 50}
            ],
            "privileged": False,
            "ipc_mode": "private",  # Isolated IPC namespace
            "tmpfs": {"/tmp": "size=100M,mode=1777"},  # Limited temp storage
            "description": "Maximum isolation for untrusted code. Slower execution.",
            "performance_penalty": "~15%"
        }
    }

    @classmethod
    def get_config(
        cls,
        level: SandboxLevel,
        cpu_cores: int,
        ram_gb: float,
        storage_gb: float = 10.0
    ) -> Dict[str, Any]:
        """
        Get complete Docker config for sandbox level.

        Args:
            level: Sandbox security level
            cpu_cores: CPU cores to allocate
            ram_gb: RAM in GB
            storage_gb: Storage limit in GB

        Returns:
            Complete Docker container config
        """
        # Start with base config
        config = cls.BASE_CONFIG.copy()

        # Add level-specific config
        level_config = cls.CONFIGS[level].copy()

        # Remove description/metadata
        level_config.pop("description", None)
        level_config.pop("performance_penalty", None)

        config.update(level_config)

        # Add resource limits
        config.update({
            "mem_limit": f"{ram_gb}g",
            "memswap_limit": f"{ram_gb}g",
            "cpu_quota": int(cpu_cores * 100000),
            "storage_opt": {"size": f"{storage_gb}G"}
        })

        logger.info(f"Generated {level.value} sandbox config: "
                   f"{cpu_cores} cores, {ram_gb}GB RAM, {storage_gb}GB storage")

        return config

    @classmethod
    def get_level_info(cls, level: SandboxLevel) -> Dict[str, str]:
        """Get human-readable info about a sandbox level."""
        config = cls.CONFIGS[level]
        return {
            "level": level.value,
            "description": config["description"],
            "performance_penalty": config["performance_penalty"],
            "network_access": "Yes" if config.get("network_mode") != "none" else "No",
            "recommended_for": cls._get_recommendation(level)
        }

    @classmethod
    def _get_recommendation(cls, level: SandboxLevel) -> str:
        """Get recommendation for when to use this level."""
        recommendations = {
            SandboxLevel.TRUSTED: "Code from trusted friends, your own code",
            SandboxLevel.STANDARD: "Most jobs, default choice",
            SandboxLevel.PARANOID: "Untrusted code, public jobs, sensitive data"
        }
        return recommendations[level]

    @classmethod
    def compare_levels(cls) -> str:
        """
        Generate comparison table of all sandbox levels.

        Returns:
            Markdown table comparing levels
        """
        table = "| Level | Description | Network | Performance | Use Case |\n"
        table += "|-------|-------------|---------|-------------|----------|\n"

        for level in SandboxLevel:
            info = cls.get_level_info(level)
            table += f"| {level.value} | {info['description']} | "
            table += f"{info['network_access']} | {info['performance_penalty']} | "
            table += f"{info['recommended_for']} |\n"

        return table


def recommend_sandbox_level(
    docker_image: str,
    is_friend_code: bool = False,
    requires_network: bool = False
) -> SandboxLevel:
    """
    Recommend sandbox level based on job characteristics.

    Args:
        docker_image: Docker image name
        is_friend_code: True if code is from trusted friend
        requires_network: True if job needs network access

    Returns:
        Recommended sandbox level
    """
    # Trusted friend code can use TRUSTED level
    if is_friend_code:
        logger.info("Recommending TRUSTED level for friend code")
        return SandboxLevel.TRUSTED

    # Jobs requiring network should use at least STANDARD
    # (PARANOID has no network)
    if requires_network:
        logger.info("Recommending STANDARD level (network required)")
        return SandboxLevel.STANDARD

    # Unknown source, recommend PARANOID
    logger.info("Recommending PARANOID level for unknown code")
    return SandboxLevel.PARANOID


# Example usage
if __name__ == "__main__":
    print("Sandbox Level Comparison:")
    print(SandboxConfig.compare_levels())

    print("\nExample Configs:")
    for level in SandboxLevel:
        config = SandboxConfig.get_config(level, cpu_cores=4, ram_gb=8.0)
        print(f"\n{level.value}:")
        print(f"  Network: {config.get('network_mode')}")
        print(f"  PIDs limit: {config.get('pids_limit')}")
        print(f"  Security opts: {config.get('security_opt')}")
