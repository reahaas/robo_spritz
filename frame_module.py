import cv2
from picamera2 import Picamera2


class Frame_Module:
    def __init__(self):
        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration({'format': 'RGB888'})
        self.picam2.configure(config)
        self.picam2.start()


    def display_camera(self, frame):
        cv2.imshow("frame", frame)
        cv2.waitKey(1)


    def get_frame(self):
            frame = self.picam2.capture_array()
            return frame
