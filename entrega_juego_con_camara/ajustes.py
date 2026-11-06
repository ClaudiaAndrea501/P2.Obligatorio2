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

CLOUD_WIDTH_RANGE = (105, 165)
CLOUD_HEIGHT_RANGE = (40, 60)
CLOUD_SPEED_RANGE = (7, 15)
CLOUD_Y_RANGE = (24, 570)
CLOUD_PIXEL_SCALE = 3
LEVEL_BANNER_SECONDS = 2.0
MAX_RANKING_ENTRIES = 10
MAX_PLAYER_NAME_LENGTH = 16
LEVELS = (
    {
        "name": "Mañana",
        "sky_top": (113, 185, 231),
        "sky_bottom": (255, 218, 180),
        "cloud_count": 8,
        "cloud_color": (255, 251, 244, 238),
        "cloud_shadow_color": (202, 158, 148, 32),
        "text_color": (40, 74, 102),
        "bottles_to_collect": 6,
    },
    {
        "name": "Mediodía",
        "sky_top": (58, 158, 229),
        "sky_bottom": (185, 226, 247),
        "cloud_count": 5,
        "cloud_color": (255, 255, 255, 240),
        "cloud_shadow_color": (123, 170, 192, 22),
        "text_color": (24, 73, 113),
        "bottles_to_collect": 12,
    },
    {
        "name": "Tarde",
        "sky_top": (235, 143, 125),
        "sky_bottom": (255, 211, 157),
        "cloud_count": 11,
        "cloud_color": (255, 239, 228, 238),
        "cloud_shadow_color": (191, 111, 121, 30),
        "text_color": (106, 57, 67),
        "bottles_to_collect": 18,
    },
    {
        "name": "Noche",
        "sky_top": (23, 39, 82),
        "sky_bottom": (68, 87, 136),
        "cloud_count": 4,
        "cloud_color": (211, 224, 246, 220),
        "cloud_shadow_color": (20, 34, 72, 48),
        "text_color": (245, 249, 255),
        "bottles_to_collect": 24,
    },
)
HAND_COLOR = (255, 190, 145)
HAND_OUTLINE_COLOR = (153, 91, 73)
HAND_HIGHLIGHT_COLOR = (255, 224, 191)
HAND_SPRITE_SIZE = (58, 68)
BOTTLE_BODY_COLOR = (103, 255, 211, 105)
BOTTLE_EDGE_COLOR = (72, 231, 183, 245)
BOTTLE_CAP_COLOR = (0, 130, 74, 255)
BOTTLE_CAP_EDGE_COLOR = (0, 88, 52, 255)
BOTTLE_HIGHLIGHT_COLOR = (222, 255, 247, 225)
BOTTLE_LABEL_COLOR = (9, 112, 90, 235)
BATTERY_BODY_COLOR = (65, 77, 89)
BATTERY_EDGE_COLOR = (36, 45, 55)
BATTERY_TERMINAL_COLOR = (222, 167, 69)
BATTERY_LABEL_COLOR = (255, 229, 164)
BATTERY_WARNING_COLOR = (242, 103, 75)
BATTERY_SPRITE_SIZE = (38, 54)
WARNING_COLOR = (255, 146, 104)
WHITE = (235, 244, 255)

PLAYER_RADIUS = 21
PLAYER_SMOOTHING = 0.24
OBJECT_RADIUS = 15
BATTERY_COLLISION_RADIUS = 18
OBJECT_SPEED_RANGE = (115, 225)
BOTTLE_SWAY = 48
BOTTLE_PHASE_SPEED = 2.5
BOTTLE_CHANCE = 0.48
BOTTLE_SPRITE_SIZE = (36, 52)
BOTTLE_COLLISION_RADIUS = 18
SPAWN_INTERVAL = 0.72
STARTING_LIVES = 3
GAME_DURATION = 75
TIME_WARNING_SECONDS = 12

CAMERA_INDEX = 0
# HSV limits for a vivid green marker, such as a sheet of green paper.
GREEN_HSV_LOWER = (30, 35, 30)
GREEN_HSV_UPPER = (100, 255, 255)
MASK_KERNEL_SIZE = 5
MIN_MARKER_AREA = 180
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

FONT_SIZE = 48
SMALL_FONT_SIZE = 30

SOUND_COLLECT_PATH = SOUNDS_DIR / "cristal.wav"
SOUND_HIT_PATH = SOUNDS_DIR / "impacto.wav"
