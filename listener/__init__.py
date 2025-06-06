from expression import curry_flip
from fastapi import WebSocket
from pythonosc.udp_client import SimpleUDPClient

from DataContainer import GazeProjection
from services.ClientManager import WSClientManager


async def osc_broadcast(event: tuple[int, GazeProjection]):
    osc = SimpleUDPClient("127.0.0.1", 5001)
    osc.send_message(f"/gaze/{event[0]}/", [event[1].coordinates.x, event[1].coordinates.y])
    osc.send_message(f"/offset/{event[0]}/", [event[1].center_offset.x, event[1].center_offset.y])


async def debug_logging(event: tuple[int, GazeProjection]):
    print(event)


def ws_feedback(manager: WSClientManager):
    async def f(event: tuple[int, GazeProjection]):
        await manager.broadcast_json({
            "id": event[0],
            "x": event[1].center_offset.x,
            "y": event[1].center_offset.y
        })

    return f
