import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for better performance (optional)
    frame = cv2.resize(frame, (640, 480))

    # Split the image into BGR channels
    B, G, R = cv2.split(frame)

    # Convert original image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Subtract grayscale from red plane
    red_diff = cv2.subtract(R, gray)

    # Apply thresholding to highlight red regions
    _, thresh = cv2.threshold(red_diff, 50, 255, cv2.THRESH_BINARY)

    # Show the intermediate and final outputs
    cv2.imshow("Original", frame)
    cv2.imshow("Red Plane", R)
    cv2.imshow("Grayscale", gray)
    cv2.imshow("Red - Gray", red_diff)
    cv2.imshow("Thresholded Red Objects", thresh)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
