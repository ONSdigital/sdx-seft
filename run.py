from pathlib import Path

from sdx_base.run import run
from sdx_base.server.server import RouterConfig

from app.routes import router
from app.services.process_service import get_tx_id
from app.settings import Settings

if __name__ == '__main__':
    proj_root = Path(__file__).parent  # sdx-seft dir
    router_config = RouterConfig(router, tx_id_getter=get_tx_id)
    run(Settings, routers=[router_config], proj_root=proj_root)
