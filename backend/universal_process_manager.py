"""
Universal process manager that works on both Emergent (supervisor) and Railway.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Detect environment
IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.getenv('RAILWAY_SERVICE_NAME') is not None

if IS_RAILWAY:
    logger.info("Detected Railway environment - using direct process management")
    from railway_process_manager import RailwayProcessManager as ProcessManager
else:
    logger.info("Detected Emergent environment - using supervisor")
    from supervisor_client import SupervisorClient as ProcessManager


class UniversalProcessManager:
    """
    Universal process manager that adapts to the environment.
    
    Uses supervisor on Emergent, direct subprocess on Railway.
    """
    
    _clawdbot_cmd: Optional[str] = None
    
    @classmethod
    def set_clawdbot_command(cls, cmd: str):
        """Set the clawdbot command path."""
        cls._clawdbot_cmd = cmd
    
    @classmethod
    def start(cls) -> bool:
        """Start the gateway process."""
        if IS_RAILWAY and cls._clawdbot_cmd:
            return ProcessManager.start(cls._clawdbot_cmd)
        return ProcessManager.start()
    
    @classmethod
    def stop(cls) -> bool:
        """Stop the gateway process."""
        return ProcessManager.stop()
    
    @classmethod
    def status(cls) -> bool:
        """Check if the gateway is running."""
        return ProcessManager.status()
    
    @classmethod
    def get_pid(cls) -> Optional[int]:
        """Get the PID of the gateway process."""
        return ProcessManager.get_pid()
    
    @classmethod
    def restart(cls) -> bool:
        """Restart the gateway process."""
        if IS_RAILWAY and cls._clawdbot_cmd:
            return ProcessManager.restart(cls._clawdbot_cmd)
        return ProcessManager.restart()
