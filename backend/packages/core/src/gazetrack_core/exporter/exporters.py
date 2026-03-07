import asyncio
from typing import Callable, Awaitable

from pythonosc.udp_client import SimpleUDPClient

from gazetrack_core.exporter import Exporter
from gazetrack_core.struct.functions import center_offset
from gazetrack_core.struct import Timestamped, Final


def osc_exporter_from(addr: str, port: int) -> Exporter[Timestamped[Final]]:
    client = SimpleUDPClient(addr, port)

    def exporter(value: Timestamped[Final]) -> None:
        final = value.unwrap()
        for projection in final.projection:
            coord = projection.gaze
            offset = center_offset(projection)
            client.send_message(f"/gaze/{projection.index}/", list(coord))
            client.send_message(f"/offset/{projection.index}/", list(offset))

    return exporter


def ws_exporter_from(
    broadcast: Callable[[dict], Awaitable[None]],
) -> Exporter[Timestamped[Final]]:
    def exporter(value: Timestamped[Final]) -> None:
        final = value.unwrap()
        projections = []
        for projection in final.projection:
            offset = center_offset(projection)
            projections.append(
                {
                    "index": projection.index,
                    "gaze": list(projection.gaze),
                    "offset": list(offset),
                }
            )
        payload = {"timestamp": value.timestamp, "projections": projections}
        asyncio.ensure_future(broadcast(payload))

    return exporter
