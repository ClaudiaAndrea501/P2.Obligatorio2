import math
import time
from typing import NamedTuple

import cv2
import pygame
from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

import ajustes


class HandState(NamedTuple):
    """Representa la posición y el gesto detectados de una mano."""

    position: tuple[int, int]
    is_slicing: bool
    radius: int


def prepare_camera_frame(frame, output_size):
    """Espeja y convierte un cuadro de cámara en una superficie de Pygame."""

    mirrored_frame = cv2.flip(frame, 1)
    rgb_background = cv2.cvtColor(mirrored_frame, cv2.COLOR_BGR2RGB)
    if (mirrored_frame.shape[1], mirrored_frame.shape[0]) == output_size:
        background_frame = rgb_background
    else:
        background_frame = cv2.resize(
            rgb_background,
            output_size,
            interpolation=(
                cv2.INTER_AREA
                if output_size[0] < mirrored_frame.shape[1]
                or output_size[1] < mirrored_frame.shape[0]
                else cv2.INTER_LINEAR
            ),
        )
    camera_surface = pygame.image.frombuffer(
        background_frame.tobytes(),
        output_size,
        "RGB",
    ).copy()
    return rgb_background, camera_surface


def hand_state_from_landmarks(landmarks):
    """Convierte los puntos de MediaPipe en posición, gesto y radio del índice."""

    screen_points = [
        (
            min(
                ajustes.WINDOW_WIDTH - ajustes.HAND_POINT_MARGIN,
                round(point.x * ajustes.WINDOW_WIDTH),
            ),
            min(
                ajustes.WINDOW_HEIGHT - ajustes.HAND_POINT_MARGIN,
                round(point.y * ajustes.WINDOW_HEIGHT),
            ),
        )
        for point in landmarks
    ]
    finger_pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
    extended_fingers = tuple(
        math.dist(screen_points[tip], screen_points[0])
        > math.dist(screen_points[pip], screen_points[0])
        * ajustes.FINGER_EXTENSION_RATIO
        for tip, pip in finger_pairs
    )
    is_slicing = extended_fingers[0] and not any(extended_fingers[1:])
    hand_width = max(point[0] for point in screen_points) - min(
        point[0] for point in screen_points
    )
    hand_height = max(point[1] for point in screen_points) - min(
        point[1] for point in screen_points
    )
    radius = max(
        ajustes.HAND_RADIUS_RANGE[0],
        min(
            ajustes.HAND_RADIUS_RANGE[1],
            round(max(hand_width, hand_height) * ajustes.HAND_RADIUS_PROPORTION),
        ),
    )
    return HandState(screen_points[8], is_slicing, radius)


class Vision:
    """Administra la cámara y el modelo de detección de manos."""

    def __init__(self, camera_index, output_size):
        """Abre la cámara y configura el detector de manos."""

        if not ajustes.HAND_MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"No se encontro el modelo de deteccion de manos: "
                f"{ajustes.HAND_MODEL_PATH}"
            )
        self.hand_landmarker = HandLandmarker.create_from_options(
            HandLandmarkerOptions(
                base_options=BaseOptions(
                    model_asset_path=str(ajustes.HAND_MODEL_PATH)
                ),
                running_mode=RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=ajustes.HAND_DETECTION_CONFIDENCE,
                min_hand_presence_confidence=ajustes.HAND_PRESENCE_CONFIDENCE,
                min_tracking_confidence=ajustes.HAND_TRACKING_CONFIDENCE,
            )
        )
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ajustes.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ajustes.CAMERA_HEIGHT)
        self.output_size = output_size
        self._last_frame_timestamp_ms = 0
        self._camera_surface = None

    @property
    def is_opened(self):
        """Indica si la cámara se abrió correctamente."""

        return self.cap.isOpened()

    @property
    def camera_surface(self):
        """Devuelve la última superficie de cámara espejada disponible."""

        return self._camera_surface

    def read_hand_state(self):
        """Lee un cuadro y devuelve el estado detectado de la mano o None."""

        success, frame = self.cap.read()
        if not success:
            self._camera_surface = None
            return None

        rgb_background, self._camera_surface = prepare_camera_frame(
            frame,
            self.output_size,
        )
        self._last_frame_timestamp_ms = max(
            self._last_frame_timestamp_ms + 1,
            time.monotonic_ns() // 1_000_000,
        )
        result = self.hand_landmarker.detect_for_video(
            Image(image_format=ImageFormat.SRGB, data=rgb_background),
            self._last_frame_timestamp_ms,
        )
        if not result.hand_landmarks:
            return None

        return hand_state_from_landmarks(result.hand_landmarks[0])

    def release(self):
        """Libera los recursos usados por la cámara y el detector."""

        self.cap.release()
        self.hand_landmarker.close()
        self._camera_surface = None
