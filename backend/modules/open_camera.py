
import cv2

def open_camera():
    """
    Open webcam using OpenCV
    Press 'q' to quit

    Returns:
        str: Status message
    """
    try:
        # Initialize camera (0 is default camera)
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Sorry, couldn't access the camera"

        print("📷 Camera opened. Press 'q' to quit.")

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                break

            # Display the frame
            cv2.imshow('EVA Camera - Press Q to quit', frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release camera and close windows
        cap.release()
        cv2.destroyAllWindows()

        return "Camera closed"

    except Exception as e:
        return f"Error opening camera: {str(e)}"
