from fastapi import WebSocket, WebSocketDisconnect, APIRouter

router = APIRouter()
active_connections = {}

@router.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    await websocket.accept()
    if doc_id not in active_connections:
        active_connections[doc_id] = []
    active_connections[doc_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for conn in active_connections[doc_id]:
                if conn != websocket:  # do NOT send back to sender
                    await conn.send_text(data)
    except WebSocketDisconnect:
        active_connections[doc_id].remove(websocket)
