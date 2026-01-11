"""Proxy configuration for H-Conductor model hierarchy.

Provides configuration for the three-tier model system:
- Flash (port 2405): Fast execution tasks
- Pro (port 2406): Planning and QA
- Opus (port 2408): Strategy and complex decisions

Environment variable overrides:
- HC_FLASH_PORT: Override flash proxy port
- HC_PRO_PORT: Override pro proxy port
- HC_OPUS_PORT: Override opus proxy port
"""

import os
from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when proxy configuration is invalid."""

    pass


@dataclass
class ModelConfig:
    """Configuration for a model proxy.

    Attributes:
        port: The port number the proxy listens on.
        base_url: Full base URL for API requests.
        name: Model identifier (flash, pro, opus).
    """

    port: int
    base_url: str
    name: str


# Default port assignments
DEFAULT_PORTS = {
    "flash": 2405,
    "pro": 2406,
    "opus": 2408,
}

# Environment variable names for port overrides
ENV_VARS = {
    "flash": "HC_FLASH_PORT",
    "pro": "HC_PRO_PORT",
    "opus": "HC_OPUS_PORT",
}

# Static PROXIES dict with default configuration
PROXIES: dict[str, ModelConfig] = {
    name: ModelConfig(
        port=port,
        base_url=f"http://localhost:{port}",
        name=name,
    )
    for name, port in DEFAULT_PORTS.items()
}


def get_proxy_config(model_name: str) -> ModelConfig:
    """Get proxy configuration for a model, respecting env overrides.

    Args:
        model_name: One of 'flash', 'pro', or 'opus'.

    Returns:
        ModelConfig with port, base_url, and name.

    Raises:
        ConfigError: If model_name is invalid or env port is malformed.
    """
    if model_name not in DEFAULT_PORTS:
        raise ConfigError(f"Unknown model: '{model_name}'. Valid: flash, pro, opus")

    # Check for environment variable override
    env_var = ENV_VARS[model_name]
    env_port = os.environ.get(env_var)

    if env_port is not None:
        try:
            port = int(env_port)
        except ValueError:
            raise ConfigError(
                f"Invalid port in {env_var}: '{env_port}'. Must be an integer."
            )
        # Validate port range
        if not (1 <= port <= 65535):
            raise ConfigError(
                f"Invalid port in {env_var}: {port}. Must be in range 1-65535."
            )
    else:
        port = DEFAULT_PORTS[model_name]

    return ModelConfig(
        port=port,
        base_url=f"http://localhost:{port}",
        name=model_name,
    )
