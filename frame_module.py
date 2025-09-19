import cv2
from picamera2 import Picamera2

class Frame_Module:
	def __init__(self):
		# Initialize camera
		self.picam2 = Picamera2()
		config =self.picam2.create_preview_configuration({'format': 'RGB888'})
		self.picam2.configure(config)
		self.picam2.start()
		
	def get_frame(self):
		try:
			frame =self.picam2.capture_array()
			return frame
		except KeyboardInterrupt:
			 print("\nStopped by user")
		finally:
			pass
			#picam2.stop()
			#cv2.destroyAllWindows()
