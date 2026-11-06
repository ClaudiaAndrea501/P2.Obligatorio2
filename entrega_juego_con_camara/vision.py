import cv2
import pygame

import ajustes


class Vision:
    def __init__(self, camera_index):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ajustes.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ajustes.CAMERA_HEIGHT)
        self._camera_surface = None
        self._last_marker = None
        self._frames_without_marker = 0

    @property
    def is_opened(self):
        return self.cap.isOpened()

    @property
    def camera_surface(self):
        return self._camera_surface

    def read_position(self):
        success, frame = self.cap.read()
        if not success:
            self._camera_surface = None
            self._last_marker = None
            self._frames_without_marker = 0
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
            interpolation=cv2.INTER_LINEAR,
        )
        self._camera_surface = pygame.image.frombuffer(
            background_frame.tobytes(),
            (ajustes.WINDOW_WIDTH, ajustes.WINDOW_HEIGHT),
            "RGB",
        ).copy()
        tracking_height, tracking_width = crop.shape[:2]
        hsv_frame = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv_frame,
            ajustes.GREEN_HSV_LOWER,
            ajustes.GREEN_HSV_UPPER,
        )
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (ajustes.MASK_KERNEL_SIZE, ajustes.MASK_KERNEL_SIZE),
        )
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        max_marker_area = (
            tracking_width * tracking_height * ajustes.MAX_MARKER_AREA_RATIO
        )
        markers = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if not ajustes.MIN_MARKER_AREA <= area <= max_marker_area:
                continue
            _, _, width, height = cv2.boundingRect(contour)
            if min(width, height) < ajustes.MIN_MARKER_SIDE:
                continue
            max_side = (
                min(tracking_width, tracking_height)
                * ajustes.MAX_MARKER_SIDE_RATIO
            )
            if max(width, height) > max_side:
                continue
            moments = cv2.moments(contour)
            if moments["m00"] == 0:
                continue
            center = (
                round(moments["m10"] / moments["m00"]),
                round(moments["m01"] / moments["m00"]),
            )
            markers.append((center, area))

        marker = self._select_marker(markers, tracking_width, tracking_height)
        if marker is None:
            self._frames_without_marker += 1
            if self._frames_without_marker > ajustes.MARKER_REACQUIRE_FRAMES:
                self._last_marker = None
            return None

        camera_position, area = marker
        self._last_marker = (camera_position, area)
        self._frames_without_marker = 0
        screen_x = round(
            camera_position[0] * ajustes.WINDOW_WIDTH / tracking_width
        )
        screen_y = round(
            camera_position[1] * ajustes.WINDOW_HEIGHT / tracking_height
        )
        screen_x = max(0, min(screen_x, ajustes.WINDOW_WIDTH - 1))
        screen_y = max(0, min(screen_y, ajustes.WINDOW_HEIGHT - 1))
        return screen_x, screen_y

    def _select_marker(self, markers, frame_width, frame_height):
        if not markers:
            return None

        if (
            self._last_marker is None
            or self._frames_without_marker > ajustes.MARKER_REACQUIRE_FRAMES
        ):
            return max(markers, key=lambda marker: marker[1])

        previous_position, previous_area = self._last_marker
        max_distance = min(frame_width, frame_height) * ajustes.MAX_MARKER_JUMP_RATIO
        candidates = []
        for position, area in markers:
            distance = cv2.norm(
                (float(position[0]), float(position[1])),
                (float(previous_position[0]), float(previous_position[1])),
            )
            if distance > max_distance:
                continue
            area_change = abs(area - previous_area) / max(area, previous_area)
            score = distance + area_change * max_distance * 0.35
            candidates.append((score, position, area))
        if not candidates:
            return None
        _, position, area = min(candidates, key=lambda candidate: candidate[0])
        return position, area

    def release(self):
        self.cap.release()
        self._camera_surface = None
        self._last_marker = None
        self._frames_without_marker = 0
