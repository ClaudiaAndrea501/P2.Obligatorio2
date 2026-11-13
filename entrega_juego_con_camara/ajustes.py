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

LEVEL_BANNER_SECONDS = 2.0
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
        "name": "Agua con gas",
        "bottle_variant": "verde_tapa_azul",
        "text_color": (24, 73, 113),
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
BOTTLE_BODY_COLOR = (103, 255, 211, 105)
BOTTLE_EDGE_COLOR = (72, 231, 183, 245)
BOTTLE_CAP_COLOR = (0, 130, 74, 255)
BOTTLE_CAP_EDGE_COLOR = (0, 88, 52, 255)
BOTTLE_HIGHLIGHT_COLOR = (222, 255, 247, 225)
BOTTLE_LABEL_COLOR = (9, 112, 90, 235)
BOTTLE_VARIANTS = {
    "verde": (
        BOTTLE_BODY_COLOR,
        BOTTLE_EDGE_COLOR,
        BOTTLE_CAP_COLOR,
        BOTTLE_CAP_EDGE_COLOR,
    ),
    "beige": ((238, 233, 216, 125), (190, 181, 155, 235), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "amarillo": ((255, 225, 65, 110), (228, 177, 30, 235), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "naranja": ((255, 112, 16, 155), (224, 76, 8, 245), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "marron_claro": ((190, 135, 88, 115), (145, 91, 54, 235), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "rosado": ((255, 120, 180, 110), (218, 65, 128, 235), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "rojo": ((242, 65, 68, 110), (182, 35, 45, 240), BOTTLE_CAP_COLOR, BOTTLE_CAP_EDGE_COLOR),
    "verde_tapa_azul": (
        BOTTLE_BODY_COLOR,
        BOTTLE_EDGE_COLOR,
        (35, 115, 220, 255),
        (16, 67, 148, 255),
    ),
}
WARNING_COLOR = (255, 146, 104)
WHITE = (235, 244, 255)

PLAYER_RADIUS = 21
PLAYER_SMOOTHING = 0.55
OBJECT_SPEED_RANGE = (115, 225)
BOTTLE_SWAY = 48
BOTTLE_PHASE_SPEED = 2.5
BOTTLE_TARGET_CHANCE = 0.5
BOTTLE_SPRITE_SIZE = (36, 52)
BOTTLE_COLLISION_RADIUS = 18
SPAWN_INTERVAL = 0.72
STARTING_LIVES = 3
TIME_WARNING_SECONDS = 12

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
HAND_MODEL_PATH = ASSETS_DIR / "models" / "hand_landmarker.task"
HAND_TOUCH_RELEASE_MARGIN = 24
CRUSHED_BOTTLE_DISPLAY_SECONDS = 0.7

FONT_SIZE = 48
SMALL_FONT_SIZE = 30

SOUND_COLLECT_PATH = SOUNDS_DIR / "cristal.wav"
SOUND_HIT_PATH = SOUNDS_DIR / "impacto.wav"
