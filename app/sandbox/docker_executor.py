import docker
import os
import tempfile
from typing import Dict, Tuple

class DockerExecutor:
    def __init__(self, image_name: str = "agent-sandbox:latest"):
        self.image_name = image_name
        self.client = docker.from_env()
        self._warm_container = None
        self._ensure_warm_container()

    def _ensure_warm_container(self):
        """Ensures a persistent warm sandbox container is active for ultra-fast execution."""
        try:
            if self._warm_container:
                self._warm_container.reload()
                if self._warm_container.status == "running":
                    return

            # Clean up any leftover warm containers
            containers = self.client.containers.list(all=True, filters={"name": "agent-sandbox-warm"})
            for c in containers:
                c.remove(force=True)

            # Start background container
            self._warm_container = self.client.containers.run(
                image=self.image_name,
                command="tail -f /dev/null",
                name="agent-sandbox-warm",
                detach=True,
                network_disabled=True,
                mem_limit="256m"
            )
        except Exception as e:
            print(f"Warning: Failed to initialize warm container pool: {e}")

    def run_pytest(self, files: Dict[str, str], timeout: int = 15) -> Tuple[int, str]:
        """
        Executes pytest inside the warm container using docker exec for sub-second execution times.
        """
        self._ensure_warm_container()

        try:
            # Clean container workdir
            self._warm_container.exec_run("rm -rf /app/*")
            
            # Write files into container
            for filename, content in files.items():
                self._warm_container.exec_run(
                    f'sh -c "cat << \'EOF\' > /app/{filename}\n{content}\nEOF"'
                )

            # Fast Pytest execution
            exec_result = self._warm_container.exec_run(
                cmd="pytest --tb=short",
                workdir="/app"
            )

            exit_code = exec_result.exit_code
            logs = exec_result.output.decode("utf-8")
            return exit_code, logs

        except Exception as e:
            print(f"Exec execution failed, reverting to fallback spin-up: {e}")
            return self._run_pytest_fallback(files, timeout)

    def _run_pytest_fallback(self, files: Dict[str, str], timeout: int = 30) -> Tuple[int, str]:
        """Fallback ephemeral container runner."""
        with tempfile.TemporaryDirectory() as temp_dir:
            for filename, content in files.items():
                file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            try:
                container = self.client.containers.run(
                    image=self.image_name,
                    command="pytest --tb=short",
                    volumes={temp_dir: {"bind": "/app", "mode": "rw"}},
                    working_dir="/app",
                    detach=True,
                    network_disabled=True,
                    mem_limit="256m"
                )
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", 1)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")
                container.remove(force=True)
                return exit_code, logs
            except Exception as e:
                return 1, f"Docker Execution Error: {str(e)}"