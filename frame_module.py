import cv2
from picamera2 import Picamera2


class Frame_Module:
    def __init__(self):
        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration({'format': 'RGB888'})
        self.picam2.configure(config)
        self.picam2.start()

    def get_frame(self):
            frame = self.picam2.capture_array()
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            return frame

def display_camera(frame, face_position = None, direction = None, center = None):

    if face_position and direction:
        # Draw a circle at the face position
        cv2.circle(frame, face_position, 20, (0, 255, 0), -1)
        cv2.circle(frame, face_position, 50, (0, 0, 255), -1)

        if center:
            cv2.circle(frame, center, 10, (255, 0, 0), -1)
            cv2.line(frame, center, face_position, (0, 255, 0), 2)

    cv2.imshow("frame", frame)

    cv2.waitKey(1)

def get_center(frame):
    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]
    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2

    return frame_center_x, frame_center_y