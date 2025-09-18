import cv2
import time
import os
from datetime import datetime
from directions_module import Directions_Module

def main():
    """
    Test the Directions_Module by calling get_face_direction method 5 times.
    Saves a picture during each test.
    """
    print("Starting Directions_Module Test")
    print("This will call get_face_direction() 5 times with 2-second intervals")
    print("Pictures will be saved for each test")
    print("Make sure your face is visible to the camera")
    print("-" * 50)
    
    # Create output directory for test images
    test_output_dir = "test_images"
    if not os.path.exists(test_output_dir):
        os.makedirs(test_output_dir)
        print(f"Created directory: {test_output_dir}")
    
    # Initialize the directions module
    directions = Directions_Module(tolerance=10)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    try:
        # Call the method 5 times
        for i in range(1, 6):
            print(f"\nTest {i}/5:")
            
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                continue
            
            # Call the get_face_direction method
            horizontal, vertical = directions.get_face_direction(frame)
            
            # Generate timestamp and filename for this test
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_output_dir}/test_{i}_{timestamp}_H{horizontal}_V{vertical}.jpg"
            
            # Save the image
            cv2.imwrite(filename, frame)
            print(f"  📸 Image saved: {filename}")
            
            # Display results
            print(f"  Horizontal: {horizontal}")
            print(f"  Vertical: {vertical}")
            
            # Interpret results
            h_direction = "RIGHT" if horizontal == -1 else "LEFT" if horizontal == 1 else "CENTERED"
            v_direction = "DOWN" if vertical == -1 else "UP" if vertical == 1 else "CENTERED"
            
            print(f"  Interpretation: Move {h_direction} (H), Move {v_direction} (V)")
            
            if horizontal == 0 and vertical == 0:
                print("  ✅ Face is PERFECTLY CENTERED!")
            else:
                print(f"  ⚠️  Face needs adjustment")
            
            # Wait 2 seconds before next test (except for the last one)
            if i < 5:
                print("  Waiting 2 seconds...")
                time.sleep(2)
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("\n" + "-" * 50)
        print("Test completed. Camera released.")

if __name__ == "__main__":
    main()
