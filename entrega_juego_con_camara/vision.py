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
    position: tuple[int, int]
    is_open: bool
    radius: int


def hand_state_from_landmarks(landmarks):
    screen_points = [
        (
            min(ajustes.WINDOW_WIDTH - 1, round(point.x * ajustes.WINDOW_WIDTH)),
            min(ajustes.WINDOW_HEIGHT - 1, round(point.y * ajustes.WINDOW_HEIGHT)),
        )
        for point in landmarks
    ]
    palm_indices = (0, 5, 9, 13, 17)
    center = (
        round(
            sum(screen_points[index][0] for index in palm_indices)
            / len(palm_indices)
        ),
        round(
            sum(screen_points[index][1] for index in palm_indices)
            / len(palm_indices)
        ),
    )
    finger_pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
    extended_fingers = sum(
        math.dist(screen_points[tip], screen_points[0])
        > math.dist(screen_points[pip], screen_points[0]) * 1.12
        for tip, pip in finger_pairs
    )
    hand_width = max(point[0] for point in screen_points) - min(
        point[0] for point in screen_points
    )
    hand_height = max(point[1] for point in screen_points) - min(
        point[1] for point in screen_points
    )
    radius = max(20, min(42, round(max(hand_width, hand_height) * 0.16)))
    return HandState(center, extended_fingers >= 3, radius)


class Vision:
    def __init__(self, camera_index):
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
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        )
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ajustes.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ajustes.CAMERA_HEIGHT)
        self._last_frame_timestamp_ms = 0
        self._camera_surface = None

    @property
    def is_opened(self):
        return self.cap.isOpened()

    @property
    def camera_surface(self):
        return self._camera_surface

    def read_hand_state(self):
        success, frame = self.cap.read()
        if not success:
            self._camera_surface = None
            return None

        mirrored_frame = cv2.flip(frame, 1)
        frame_height, frame_width = mirrored_frame.shape[:2]
        scale = max(
            ajustes.WINDOW_WIDTH / frame_width,
            ajustes.WINDOW_HEIGHT / frame_height,
        )
        visible_width = ajustes.WINDOW_WIDTH / scale
        visible_height = ajustes.WINDOW_HEIGHT / scale
        crop_left = round((frame_width - visible_width) / 2)
        crop_top = round((frame_height - visible_height) / 2)
        crop_right = round(crop_left + visible_width)
        crop_bottom = round(crop_top + visible_height)
        crop = mirrored_frame[
            crop_top:crop_bottom,
            crop_left:crop_right,
        ]
        rgb_background = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        background_frame = cv2.resize(
            rgb_background,
            (ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT),
            interpolation=(
                cv2.INTER_AREA
                if crop.shape[1] > ajustes.WINDOW_WIDTH
                or crop.shape[0] > ajustes.WINDOW_HEIGHT
                else cv2.INTER_CUBIC
            ),
        )
        self._camera_surface = pygame.image.frombuffer(
            background_frame.tobytes(),
            (ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT),
            "RGB",
        ).copy()
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
        self.cap.release()
        self.hand_landmarker.close()
        self._camera_surface = None
