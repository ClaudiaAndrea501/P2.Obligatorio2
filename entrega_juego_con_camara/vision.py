import cv2

import ajustes


class Vision:
    def __init__(self, camera_index):
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ajustes.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ajustes.CAMERA_HEIGHT)

    @property
    def is_opened(self):
        return self.cap.isOpened()

    def read_position(self):
        success, frame = self.cap.read()
        if not success:
            return None

        mirrored_frame = cv2.flip(frame, 1)
        hsv_frame = cv2.cvtColor(mirrored_frame, cv2.COLOR_BGR2HSV)
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
        if not contours:
            return None

        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) < ajustes.MIN_MARKER_AREA:
            return None

        moments = cv2.moments(largest_contour)
        if moments["m00"] == 0:
            return None

        camera_x = int(moments["m10"] / moments["m00"])
        camera_y = int(moments["m01"] / moments["m00"])
        frame_height, frame_width = mirrored_frame.shape[:2]
        screen_x = int(camera_x * ajustes.WINDOW_WIDTH / frame_width)
        screen_y = int(camera_y * ajustes.WINDOW_HEIGHT / frame_height)
        return screen_x, screen_y

    def release(self):
        self.cap.release()
