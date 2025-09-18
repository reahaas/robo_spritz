import cv2

class Directions_Module:
    """
    A class for face detection and directional guidance calculation.
    
    This module detects faces in camera frames and calculates directional
    parameters (horizontal and vertical) relative to the frame center.
    """
    
    def __init__(self, tolerance=10):
        """
        Initialize the Directions_Module.
        
        Args:
            tolerance (int): Pixel tolerance for centering detection (default: 10)
        """
        self.tolerance = tolerance
        
        # Load the face detection classifier
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if self.face_cascade.empty():
            raise ValueError("Failed to load face detection classifier")
    
    def get_face_direction(self, frame):
        """
        Detect faces in the given frame and calculate directional parameters.
        Uses the exact same logic as camera_capture.py for consistency.
        
        Args:
            frame: OpenCV image frame (BGR format)
            
        Returns:
            tuple: (horizontal, vertical)
            - horizontal (int): 1 (face right), -1 (face left), 0 (centered)
            - vertical (int): 1 (face above), -1 (face below), 0 (centered)
        """
        if frame is None:
            return 0, 0
        
        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get frame dimensions
        frame_height, frame_width = frame.shape[:2]
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2
        
        # Detect faces in the frame (same parameters as camera_capture.py)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Initialize default values
        horizontal, vertical = 0, 0
        face_center_x, face_center_y = None, None
        
        # Process faces (using same logic as camera_capture.py)
        for (x, y, w, h) in faces:
            # Calculate face center (use the first detected face for guidance)
            if face_center_x is None:
                face_center_x = x + w // 2
                face_center_y = y + h // 2
        
        if face_center_x is not None:
            # Calculate offsets
            offset_x = face_center_x - frame_center_x
            offset_y = face_center_y - frame_center_y
            
            # Calculate numerical direction parameters
            # Horizontal: 1 if face is to the right, -1 if to the left, 0 if within tolerance
            if abs(offset_x) > self.tolerance:
                horizontal = 1 if offset_x > 0 else -1
            else:
                horizontal = 0
            
            # Vertical: 1 if face is above center, -1 if below center, 0 if within tolerance
            if abs(offset_y) > self.tolerance:
                vertical = 1 if offset_y < 0 else -1  # Negative offset_y means face is above center
            else:
                vertical = 0
        
        return horizontal, vertical
