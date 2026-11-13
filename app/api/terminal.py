import asyncio
import docker
import _thread
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()
    raw_socket = None

    try:
        client = docker.from_env()
        container = client.containers.get("agent-sandbox-warm")
        if container.status != "running":
            container.start()

        exec_instance = client.api.exec_create(
            container.id,
            cmd="/bin/bash",
            tty=True,
            stdin=True,
            stdout=True,
            stderr=True,
            workdir="/app",
            user="root"
        )

        sock = client.api.exec_start(exec_instance["Id"], socket=True)
        # Windows returns NpipeSocket directly; Linux/Mac wraps it with _sock
        raw_socket = getattr(sock, "_sock", sock)

        def stream_docker_to_ws():
            try:
                while True:
                    data = raw_socket.recv(1024)
                    if not data:
                        break
                    text = data.decode("utf-8", errors="ignore")
                    asyncio.run_coroutine_threadsafe(websocket.send_text(text), loop)
            except Exception:
                pass

        _thread.start_new_thread(stream_docker_to_ws, ())

        while True:
            msg = await websocket.receive_text()
            raw_socket.send(msg.encode("utf-8"))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"\r\nTerminal Connection Error: {str(e)}\r\n")
    finally:
        if raw_socket:
            try:
                raw_socket.close()
            except Exception:
                pass