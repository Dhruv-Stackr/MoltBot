"""
Railway-compatible process manager for clawdbot gateway.

Since Railway doesn't use supervisor, this manages the gateway
as a background subprocess.
"""

import subprocess
import logging
import os
import signal
import time
from typing import Optional

logger = logging.getLogger(__name__)


class RailwayProcessManager:
    """Manages clawdbot gateway as a background process on Railway."""

    # Store process globally (singleton pattern)
    _process: Optional[subprocess.Popen] = None
    _pid_file = "/tmp/clawdbot-gateway.pid"

    @classmethod
    def start(cls, clawdbot_cmd: str) -> bool:
        """
        Start the gateway as a background process.

        Args:
            clawdbot_cmd: Path to clawdbot executable

        Returns:
            True if started successfully, False otherwise.
        """
        try:
            # Check if already running
            if cls.is_running():
                logger.info("Gateway already running")
                return True

            logger.info(f"Starting clawdbot gateway: {clawdbot_cmd}")

            # Start process in background
            cls._process = subprocess.Popen(
                [clawdbot_cmd, "host"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Detach from parent
            )

            # Save PID
            with open(cls._pid_file, 'w') as f:
                f.write(str(cls._process.pid))

            # Give it a moment to start
            time.sleep(2)

            # Check if it's still running
            if cls._process.poll() is None:
                logger.info(f"Gateway started successfully (PID: {cls._process.pid})")
                return True
            else:
                # Process died, get error output
                stdout, stderr = cls._process.communicate(timeout=1)
                logger.error(f"Gateway process died immediately after start")
                logger.error(f"Exit code: {cls._process.returncode}")
                if stdout:
                    logger.error(f"Stdout: {stdout.decode('utf-8', errors='ignore')}")
                if stderr:
                    logger.error(f"Stderr: {stderr.decode('utf-8', errors='ignore')}")
                return False

        except Exception as e:
            logger.error(f"Error starting gateway: {e}")
            return False

    @classmethod
    def stop(cls) -> bool:
        """
        Stop the gateway process.

        Returns:
            True if stopped successfully, False otherwise.
        """
        try:
            pid = cls.get_pid()
            if pid is None:
                logger.info("Gateway not running")
                return True

            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to gateway (PID: {pid})")
                
                # Wait for graceful shutdown
                for _ in range(10):
                    try:
                        os.kill(pid, 0)  # Check if still exists
                        time.sleep(0.5)
                    except ProcessLookupError:
                        break
                else:
                    # Force kill if still running
                    os.kill(pid, signal.SIGKILL)
                    logger.warning(f"Force killed gateway (PID: {pid})")

            except ProcessLookupError:
                logger.info("Gateway process already stopped")

            # Clean up
            cls._process = None
            if os.path.exists(cls._pid_file):
                os.remove(cls._pid_file)

            return True

        except Exception as e:
            logger.error(f"Error stopping gateway: {e}")
            return False

    @classmethod
    def status(cls) -> bool:
        """
        Check if the gateway is running.

        Returns:
            True if running, False otherwise.
        """
        return cls.is_running()

    @classmethod
    def is_running(cls) -> bool:
        """Check if process is running."""
        pid = cls.get_pid()
        if pid is None:
            return False

        try:
            os.kill(pid, 0)  # Signal 0 just checks existence
            return True
        except ProcessLookupError:
            return False

    @classmethod
    def get_pid(cls) -> Optional[int]:
        """
        Get the PID of the running gateway process.

        Returns:
            The PID if running, None otherwise.
        """
        # Try from stored process object
        if cls._process and cls._process.poll() is None:
            return cls._process.pid

        # Try from PID file
        if os.path.exists(cls._pid_file):
            try:
                with open(cls._pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    # Verify it's still running
                    try:
                        os.kill(pid, 0)
                        return pid
                    except ProcessLookupError:
                        os.remove(cls._pid_file)
            except Exception:
                pass

        return None

    @classmethod
    def restart(cls, clawdbot_cmd: str) -> bool:
        """
        Restart the gateway.

        Args:
            clawdbot_cmd: Path to clawdbot executable

        Returns:
            True if restarted successfully, False otherwise.
        """
        cls.stop()
        time.sleep(1)
        return cls.start(clawdbot_cmd)
