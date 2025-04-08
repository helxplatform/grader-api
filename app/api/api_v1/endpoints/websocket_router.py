from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, Depends
from sqlalchemy.orm import Session
from websockets.exceptions import ConnectionClosed
from app.core.dependencies import get_db, PermissionDependency, RequireLoginPermission
from app.services import WebsocketManagerService

router = APIRouter()

@router.websocket("/websocket")
async def accept_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(RequireLoginPermission))
):
    websocket_manager = WebsocketManagerService(db)
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket_manager.handle_client_message(websocket)
            
    except (WebSocketDisconnect, ConnectionClosed) as e:
        # NOTE: `WebSocketDisconnect` and `ConnectionClosed` are both expected errors that may be thrown.
        await websocket_manager.disconnect(websocket)
    
    except Exception as e:
        # We could be doing some more complex logic here, but simply disconnecting the client is sufficient.
        await websocket_manager.disconnect(websocket)