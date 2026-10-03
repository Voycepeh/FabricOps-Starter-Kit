"""Microsoft Fabric Data Agent accelerator."""

from .create_data_agent import create_data_agent
from .shared import FabricDataAgentError

__all__ = ["FabricDataAgentError", "create_data_agent"]
