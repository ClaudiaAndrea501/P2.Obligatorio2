from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
RANKING_PATH = BASE_DIR / "ranking.json"

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
WINDOW_TITLE = "Orbita Verde: Rescate estelar"
FULLSCREEN = True
FPS = 60
MAX_DELTA_TIME = 0.05

LEVEL_BANNER_SECONDS = 4.0
MAX_RANKING_ENTRIES = 5
MAX_PLAYER_NAME_LENGTH = 16
LEVELS = (
    {
        "name": "Agua sin gas",
        "bottle_variant": "verde",
        "text_color": (40, 74, 102),
        "bottles_to_collect": 6,
        "time_limit": 32,
    },
    {
        "name": "Sabor uva",
        "bottle_variant": "uva",
        "text_color": (92, 48, 122),
        "bottles_to_collect": 6,
        "time_limit": 32,
    },
    {
        "name": "Sabor limón",
        "bottle_variant": "beige",
        "text_color": (106, 57, 67),
        "bottles_to_collect": 8,
        "time_limit": 38,
    },
    {
        "name": "Sabor ananá",
        "bottle_variant": "amarillo",
        "text_color": (245, 249, 255),
        "bottles_to_collect": 10,
        "time_limit": 43,
    },
    {
        "name": "Sabor pomelo rosado",
        "bottle_variant": "rosado",
        "text_color": (245, 249, 255),
        "bottles_to_collect": 12,
        "time_limit": 48,
    },
    {
        "name": "Sabor manzana",
        "bottle_variant": "marron_claro",
        "text_color": (245, 249, 255),
        "bottles_to_collect": 14,
        "time_limit": 53,
    },
    {
        "name": "Sabor frutilla",
        "bottle_variant": "rojo",
        "text_color": (245, 249, 255),
        "bottles_to_collect": 16,
        "time_limit": 58,
    },
    {
        "name": "Sabor naranja",
        "bottle_variant": "naranja",
        "text_color": (245, 249, 255),
        "bottles_to_collect": 18,
        "time_limit": 63,
    },
)
BOTTLE_BODY_COLOR = (103, 255, 211, 255)
BOTTLE_EDGE_COLOR = (38, 177, 135, 255)
BOTTLE_CAP_COLOR = (0, 130, 74, 255)
BOTTLE_CAP_EDGE_COLOR = (0, 88, 52, 255)
BOTTLE_HIGHLIGHT_COLOR = (245, 255, 249, 255)
BOTTLE_VARIANTS = {
    "verde": (
        BOTTLE_BODY_COLOR,
        BOTTLE_EDGE_COLOR,
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "beige": (
        (238, 233, 216, 255),
        (170, 151, 108, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "amarillo": (
        (255, 225, 65, 255),
        (205, 151, 15, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "naranja": (
        (255, 112, 16, 255),
        (201, 66, 8, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "marron_claro": (
        (190, 135, 88, 255),
        (126, 78, 43, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "rosado": (
        (255, 120, 180, 255),
        (195, 47, 114, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "rojo": (
        (242, 65, 68, 255),
        (178, 29, 39, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "uva": (
        (170, 95, 220, 255),
        (112, 52, 158, 255),
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
}
WARNING_COLOR = (255, 146, 104)
WHITE = (235, 244, 255)

PLAYER_RADIUS = 21
PLAYER_SMOOTHING = 0.55
OBJECT_SPEED_RANGE = (115, 225)
BOTTLE_SWAY = 48
BOTTLE_SIDE_MARGIN = 200
BOTTLE_PHASE_SPEED = 2.5
BOTTLE_TARGET_CHANCE = 0.5
BOTTLE_SPRITE_SIZE = (54, 78)
BOTTLE_COLLISION_RADIUS = 27
SPAWN_INTERVAL = 0.72
STARTING_LIVES = 3
TIME_WARNING_SECONDS = 12

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
HAND_MODEL_PATH = ASSETS_DIR / "models" / "hand_landmarker.task"
CRUSHED_BOTTLE_DISPLAY_SECONDS = 0.7

FONT_SIZE = 48
SMALL_FONT_SIZE = 30

SOUND_COLLECT_PATH = SOUNDS_DIR / "cristal.wav"
SOUND_HIT_PATH = SOUNDS_DIR / "impacto.wav"
