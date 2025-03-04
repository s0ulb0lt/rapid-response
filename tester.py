import cv2

# Open the default camera
cam = cv2.VideoCapture(cv2.CAP_MSMF)

while True:
    ret, frame = cam.read()

    # Write the frame to the output file

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()
