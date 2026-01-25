from .start import router as start_router
from .quiz import router as quiz_router
from .utils import router as utils_router
from .commands import router as commands_router
from .find_game import router as find_game_router
from .gotd import router as gotd_router

from .admin.cache_control import router as admin_cache_router
from .admin.gifts import router as admin_gifts_router
from .admin.menu import router as admin_menu_router
from .admin.sender import router as admin_sender_router
from .admin.stats import router as admin_stats_router
from .admin.reload import router as admin_reload_router

routers = [
    start_router,
    quiz_router,
    utils_router,
    commands_router,
    find_game_router,
    gotd_router,

    admin_cache_router,
    admin_gifts_router,
    admin_menu_router,
    admin_sender_router,
    admin_stats_router,
    admin_reload_router,
]