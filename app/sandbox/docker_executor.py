import docker
import base64

class DockerExecutor:
    def __init__(self, container_name: str = "agent-sandbox-warm"):
        self.container_name = container_name
        self.client = None

    def _get_client(self):
        """Lazily connects to Docker daemon so FastAPI never crashes on startup."""
        if self.client is None:
            self.client = docker.from_env()
        return self.client

    def run_tests(self, files: dict) -> tuple[int, str]:
        try:
            client = self._get_client()
            
            # 1. Auto-start or create the warm container if stopped/missing
            try:
                container = client.containers.get(self.container_name)
                if container.status != "running":
                    container.start()
            except docker.errors.NotFound:
                container = client.containers.run(
                    "python:3.11-slim",
                    command="tail -f /dev/null",
                    name=self.container_name,
                    working_dir="/app",
                    detach=True
                )

            # 2. Guarantee pytest is installed even in pre-existing containers
            check_pytest = container.exec_run("python -m pytest --version", user="root")
            if check_pytest.exit_code != 0:
                container.exec_run("pip install --no-cache-dir pytest", user="root")

            # 3. Wipe old workspace files cleanly using sh -c so wildcards expand
            container.exec_run("sh -c 'rm -rf /app/* /app/.[!.]*'", workdir="/app", user="root")
            
            # 4. Inject generated files via Base64 (supports nested directories)
            for filename, content in files.items():
                clean_name = filename.strip().lstrip("/")
                if "/" in clean_name:
                    folder = "/".join(clean_name.split("/")[:-1])
                    container.exec_run(f"mkdir -p /app/{folder}", workdir="/app", user="root")
                b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
                write_cmd = f"sh -c 'echo {b64_content} | base64 -d > /app/{clean_name}'"
                container.exec_run(write_cmd, workdir="/app", user="root")

            # 5. Install dependencies if requirements.txt exists
            install_logs = ""
            if "requirements.txt" in files and files["requirements.txt"].strip():
                pip_res = container.exec_run(
                    "pip install --no-cache-dir -r requirements.txt",
                    workdir="/app",
                    user="root"
                )
                install_logs = f"--- PIP INSTALL LOGS ---\n{pip_res.output.decode('utf-8', errors='ignore')}\n\n"

            # 6. Run Pytest with explicit PYTHONPATH=/app so local imports always resolve
            exec_res = container.exec_run(
                "sh -c 'PYTHONPATH=/app python -m pytest -v'",
                workdir="/app",
                user="root"
            )
            
            exit_code = exec_res.exit_code
            test_logs = exec_res.output.decode("utf-8", errors="ignore")
            
            return exit_code, f"{install_logs}--- PYTEST EXECUTION LOGS ---\n{test_logs}"

        except Exception as e:
            self.client = None
            return -1, (
                f"Docker Execution Exception: {str(e)}\n\n"
                "👉 Make sure Docker Desktop is open and the Engine is running!"
            )