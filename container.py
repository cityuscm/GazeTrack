import wireup

import services

container = wireup.create_async_container(
    service_modules=[services]
)
