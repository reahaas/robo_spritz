import cv2
import time
import os
from datetime import datetime

def capture_images():
    """
    Captures images from the default camera when a face is detected
    and saves them with timestamp filenames and face rectangles drawn.
    """
    # Create output directory if it doesn't exist
    output_dir = "captured_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize camera capture (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Load the face detection classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    print("Camera opened successfully!")
    print("Face detection enabled - images will only be saved when faces are detected")
    print("Directional guidance enabled - directions will be given every 2 seconds")
    print("Press 'q' to quit or Ctrl+C to stop")
    print(f"Images will be saved to '{output_dir}' directory")
    
    last_save_time = 0
    save_interval = 5  # Save interval in seconds
    
    last_direction_time = 0
    direction_interval = 2  # Direction output interval in seconds
    tolerance = 10  # Pixel tolerance for centering
    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture image")
                break
            
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Get frame dimensions
            frame_height, frame_width = frame.shape[:2]
            frame_center_x = frame_width // 2
            frame_center_y = frame_height // 2
            
            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangles around detected faces and calculate centers
            display_frame = frame.copy()
            face_center_x, face_center_y = None, None
            
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Calculate face center (use the first detected face for guidance)
                if face_center_x is None:
                    face_center_x = x + w // 2
                    face_center_y = y + h // 2
                    # Draw face center point
                    cv2.circle(display_frame, (face_center_x, face_center_y), 5, (0, 255, 0), -1)
            
            # Draw frame center point for reference
            cv2.circle(display_frame, (frame_center_x, frame_center_y), 5, (0, 0, 255), -1)
            cv2.circle(display_frame, (frame_center_x, frame_center_y), tolerance, (0, 0, 255), 2)
            
            # Calculate directional parameters and save conditions
            current_time = time.time()
            horizontal, vertical = 0, 0  # Default values
            
            if face_center_x is not None:
                # Calculate offsets
                offset_x = face_center_x - frame_center_x
                offset_y = face_center_y - frame_center_y
                
                # Calculate numerical direction parameters
                # Horizontal: 1 if face is to the right, -1 if to the left, 0 if within tolerance
                if abs(offset_x) > tolerance:
                    horizontal = 1 if offset_x > 0 else -1
                else:
                    horizontal = 0
                
                # Vertical: 1 if face is above center, -1 if below center, 0 if within tolerance
                if abs(offset_y) > tolerance:
                    vertical = 1 if offset_y < 0 else -1  # Negative offset_y means face is above center
                else:
                    vertical = 0
                
                # Provide directional guidance every 2 seconds
                if (current_time - last_direction_time) >= direction_interval:
                    print(f"Direction - Horizontal: {horizontal}, Vertical: {vertical} (Face offset: X={offset_x}, Y={offset_y})")
                    last_direction_time = current_time
            
            # Check if faces are detected, face is centered, and enough time has passed for saving
            if (len(faces) > 0 and horizontal == 0 and vertical == 0 and 
                (current_time - last_save_time) >= save_interval):
                # Generate timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_dir}/face_centered_{timestamp}.jpg"
                
                # Save the frame with face rectangles drawn
                cv2.imwrite(filename, display_frame)
                print(f"Face CENTERED! Image saved: {filename}")
                last_save_time = current_time
            
            # Display the frame with face rectangles
            cv2.imshow('Camera Feed - Face Detection', display_frame)
            
            # Check for 'q' key press (check every 30ms for responsiveness)
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                print("Quit key pressed. Stopping...")
                break
                
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Stopping...")
    
    finally:
        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released and windows closed.")

if __name__ == "__main__":
    capture_images()
