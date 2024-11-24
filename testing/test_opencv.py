import cv2
import numpy as np

# Create a blank image
image = np.zeros((500, 500, 3), dtype="uint8")

# Draw a red circle
cv2.circle(image, (250, 250), 100, (0, 0, 255), -1)

# Display the image
cv2.imshow("Test Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

