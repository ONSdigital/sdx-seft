from pathlib import Path

from sdx_base.errors.errors import UnrecoverableError
from sdx_base.run import run
from sdx_base.server.server import RouterConfig
from fastapi import Request
from sdx_base.models.pubsub import Message, get_message

from app.routes import router
from app.settings import Settings, ROOT


async def txid_from_filename(request: Request) -> str:
    message: Message = await get_message(request)
    filename = message["attributes"].get("objectId")

    if filename is None:
        raise UnrecoverableError("No object_id in attributes")

    tx_id = filename.split(".")[0]
    return tx_id

if __name__ == '__main__':
    router_config = RouterConfig(router, tx_id_getter=txid_from_filename)
    run(Settings, routers=[router_config], proj_root=ROOT)
