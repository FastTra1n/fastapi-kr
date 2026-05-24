from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query

app = FastAPI()

class RoomManager:
    def __init__(self):
        self.rooms: dict[str, dict[str, WebSocket]] = {}
    
    async def connect(self, room_id: str, username: str, ws: WebSocket):
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        if username in self.rooms[room_id]:
            await ws.close(code=1008)
        
        await ws.accept()
        self.rooms[room_id][username] = ws
    
    def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        if room_id not in self.rooms:
            return
        
        for _, ws in list(self.rooms[room_id].items()):
            await ws.send_json(payload)
    
    def get_users(self, room_id: str):
        return list(self.rooms.get(room_id, {}).keys())

manager = RoomManager()

@app.websocket("/ws/rooms/{room_id}")
async def ws_room(
    ws: WebSocket,
    room_id: str,
    username: str = Query(None)
):
    if not username or not username.strip():
        await ws.close(code=1008)
    
    await manager.connect(room_id, username, ws)
    await manager.broadcast(room_id, {
        "type": "join",
        "room_id": room_id,
        "username": username
    })
    try:
        while True:
            msg = await ws.receive_json()
            text = msg.get("text", "")
            if len(text) > 300:
                await ws.send_json({
                    "type": "error",
                    "detail": "Message is too long"
                })
            else:
                await manager.broadcast(room_id, {
                    "type": "message", 
                    "room_id": room_id,
                    "username": username,
                    "text": text
                    })
    except WebSocketDisconnect:
        manager.disconnect(room_id, username)
        await manager.broadcast(room_id, {
            "type": "left",
            "room_id": room_id,
            "username": username
        })

@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    return {
        "room_id": room_id,
        "users": manager.get_users(room_id)
    }