import asyncio
import contextlib

import wireup
from cyndilib import Finder
from pupil_labs.realtime_api import discover_devices, Device
from wireup import Injected

from container import container
from type import ClientList


@wireup.inject_from_container(container=container)
async def device_discovery(clients: Injected[ClientList]):
    with contextlib.suppress(asyncio.CancelledError):
        async for info in discover_devices():
            async with Device.from_discovered_device(info) as device:
                status = await device.get_status()
                sensor_gaze = status.direct_gaze_sensor()
                sensor_world = status.direct_world_sensor()
                if sensor_gaze.connected and sensor_world.connected:
                    clients[device.address] = (sensor_world.url, sensor_gaze.url)


@wireup.inject_from_container(container=container)
async def ndi_discovery(finder: Injected[Finder]):
    try:
        while True:
            print(finder.get_source_names())
            print(finder)
            finder.update_sources()
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
