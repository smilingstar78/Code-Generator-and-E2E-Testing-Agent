import docker
import os
import tempfile
from typing import Dict, Tuple
from app.core.config import settings

def run_code_in_sandbox(files: Dict[str, str], timeout: int = None) -> Tuple[int, str]:
    """
    Mounts generated files into a temporary directory, spins up an isolated,
    hardened Docker container using pre-built image, and runs pytest.
    """
    timeout = timeout or settings.CONTAINER_TIMEOUT_SECONDS
    client = docker.from_env()

    # Create an isolated temporary directory on the host machine
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write generated files into temp_dir
        for file_path, content in files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        try:
            # Run the pre-built, hardened sandbox container
            container = client.containers.run(
                image="agent-sandbox:latest",
                command="pytest --tb=short",
                volumes={
                    temp_dir: {"bind": "/app", "mode": "rw"}
                },
                working_dir="/app",
                detach=True,
                # --- SECURITY & HARDENING BOUNDARIES ---
                network_disabled=True,       # Blocks all outbound/inbound network traffic
                mem_limit="256m",            # Caps RAM at 256MB
                nano_cpus=1000000000,        # Limits CPU usage to 1.0 CPU core max
                cap_drop=["ALL"],            # Drops all Linux kernel privileges
                user="sandboxuser"           # Executes as non-root user
            )

            # Wait for execution or trigger timeout
            result = container.wait(timeout=timeout)
            logs = container.logs().decode("utf-8")
            container.remove(force=True)
            
            return result["StatusCode"], logs

        except docker.errors.ContainerError as ce:
            return 1, f"Container Error: {str(ce)}"
        except Exception as e:
            # Clean up lingering containers on timeout/error
            try:
                container.remove(force=True)
            except Exception:
                pass
            return 1, f"Execution timed out or failed: {str(e)}"