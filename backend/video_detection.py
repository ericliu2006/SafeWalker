import cv2
from ultralytics import YOLO
import numpy as np
import pyttsx3  # For text-to-speech

# Global variables
previous_signal_status = None
previous_message = None
engine = pyttsx3.init()
is_speaking = False  # Track if the engine is currently speaking

# Initialize the YOLOv8 model
model = YOLO('yolov8n.pt')  # Use yolov8n.pt for faster inference, or yolov8s.pt for better accuracy

# Frame skip and count for performance
frame_skip = 1  # Number of frames to skip
frame_count = 0  # Initialize frame count
vehicle_cross = True  # Vehicle cross status

# Bounding box size parameters for first-person perspective
center_box_width_ratio = 0.4  # Central vertical region (40% width)
center_box_height_ratio = 0.833  # 83.3% of the total height

# Initialize video capture
cap = cv2.VideoCapture(0)  # Replace with your video file or use 0 for webcam

def detect_color(roi):
    """Detect if the pedestrian signal is showing a 'red hand' (stop) or 'green person' (walk)."""
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Define HSV ranges for red (stop) and white (walk)
    red_lower = np.array([0, 79, 69])
    red_upper = np.array([10, 255, 255])
    lower_white = np.array([0, 0, 200])  # Lower bound of white
    upper_white = np.array([180, 30, 255])  # Upper bound of white

    # Create masks to detect colors in the ROI
    red_mask = cv2.inRange(hsv, red_lower, red_upper)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)

    red_pixels = cv2.countNonZero(red_mask)
    white_pixels = cv2.countNonZero(white_mask)

    if red_pixels > white_pixels:
        return "Do not cross the street"
    elif white_pixels > red_pixels:
        return "You are clear to cross"
    else:
        return " "

def speak_non_blocking(message):
    """Speak the message asynchronously without blocking the video."""
    global previous_message, is_speaking

    if message != previous_message and not is_speaking:
        is_speaking = True
        previous_message = message

        def on_speech_done(name, completed):
            """Reset speaking flag once the speech is done."""
            global is_speaking
            is_speaking = False

        engine.connect('finished-utterance', on_speech_done)
        engine.say(message)
        engine.iterate()  # Continue the non-blocking speech loop

# Start the speech loop non-blocking
engine.startLoop(False)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Frame capture failed.")
        break

    frame_height, frame_width = frame.shape[:2]

    # Define the center vertical bounding box coordinates
    box_x1 = int(frame_width * (1 - center_box_width_ratio) / 2)
    box_x2 = int(frame_width * (1 + center_box_width_ratio) / 2)
    box_y1 = int(frame_height * (1 - center_box_height_ratio) / 2)  # Reduced from the top
    box_y2 = int(frame_height * (1 + center_box_height_ratio) / 2)  # Reduced from the bottom

    # Only process every 'frame_skip' frames
    if frame_count % frame_skip == 0:
        # Apply YOLOv8 to detect objects in the frame
        results = model(frame, conf=0.2, show=False)

        # Draw the vertical bounding box (for visualization)
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 255, 0), 2)

        # Loop through the detected objects
        for result in results:
            for box in result.boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Convert float to int
                class_id = int(box.cls[0])  # Get the class ID of the detected object

                # Check if the object is within the defined vertical bounding box
                if x1 >= box_x1 and x2 <= box_x2 and y1 >= box_y1 and y2 <= box_y2:
                    # Inside the vertical bounding box: detect traffic signals
                    if class_id == 9:  # Assuming class ID 9 is for traffic signals
                        roi = frame[y1:y2, x1:x2]  # Crop the ROI for color detection
                        signal_status = detect_color(roi)
                        signal_color = (0, 255, 0) if signal_status == "You are clear to cross" else (0, 0, 255)
                        cv2.putText(frame, signal_status, (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, signal_color, 2)

                        if signal_status and signal_status != previous_signal_status:
                            speak_non_blocking(signal_status)
                            previous_signal_status = signal_status
                else:
                    # Outside the vertical bounding box: detect vehicles
                    if class_id in [1, 2, 3, 5, 7, 11]:  # IDs for vehicles
                        color = (255, 0, 0)  # Red for vehicles
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        # Calculate the area of the detected vehicle's bounding box
                        vehicle_area = (x2 - x1) * (y2 - y1)
                        central_box_area = (box_x2 - box_x1) * (box_y2 - box_y1)

                        # If the vehicle's area is more than 1/4 of the central bounding box area
                        if vehicle_area > central_box_area / 4:  
                            speak_non_blocking("Be careful, potential vehicle ahead.")
                            vehicle_cross = False

                    if not vehicle_cross and not is_speaking:
                        speak_non_blocking("Vehicle has moved")
                        vehicle_cross = True

    frame_count += 1  # Increment frame count

    # Display the frame with detections
    cv2.imshow('Traffic Sign and Vehicle Detection', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()

# Stop the speech engine
engine.endLoop()
