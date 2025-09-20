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
            return frame

def display_camera(frame, face_position = None, direction = None):

    if face_position and direction:
        # Draw a circle at the face position
        cv2.circle(frame, face_position, 10, (0, 255, 0), -1)
        cv2.line(frame, face_position, face_position, (0, 255, 0), 1)

    cv2.imshow("frame", frame)

    cv2.waitKey(1)
