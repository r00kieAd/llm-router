import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState


@dataclass
class ConnectionState:
    username: str
    websocket: WebSocket
    connected_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    send_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self._by_user: dict[str, set[WebSocket]] = defaultdict(set)
        self._states: dict[WebSocket, ConnectionState] = {}
        self._lock = asyncio.Lock()

    async def connect(self, username: str, websocket: WebSocket) -> ConnectionState:
        await websocket.accept()
        state = ConnectionState(username=username, websocket=websocket)
        async with self._lock:
            self._states[websocket] = state
            self._by_user[username].add(websocket)
        return state

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            state = self._states.pop(websocket, None)
            if not state:
                return
            sockets = self._by_user.get(state.username)
            if sockets:
                sockets.discard(websocket)
                if not sockets:
                    self._by_user.pop(state.username, None)

    def state(self, websocket: WebSocket) -> ConnectionState | None:
        return self._states.get(websocket)

    def touch(self, websocket: WebSocket) -> None:
        state = self._states.get(websocket)
        if state:
            state.last_seen = time.time()

    async def send(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        state = self._states.get(websocket)
        if not state:
            return
        if websocket.application_state != WebSocketState.CONNECTED:
            await self.disconnect(websocket)
            return
        async with state.send_lock:
            try:
                await websocket.send_json(message)
            except Exception as exc:
                print(f"[websocket] dropping disconnected socket after send failure: {type(exc).__name__}: {exc}")
                await self.disconnect(websocket)

    async def send_to_user(self, username: str, message: dict[str, Any]) -> None:
        sockets = list(self._by_user.get(username, set()))
        await asyncio.gather(
            *(self.send(socket, message) for socket in sockets),
            return_exceptions=True,
        )

    def user_connection_count(self, username: str) -> int:
        return len(self._by_user.get(username, set()))


manager = WebSocketConnectionManager()
