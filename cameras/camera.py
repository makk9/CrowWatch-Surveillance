import cv2

class Camera:
    def __init__(self, device_index):
        """
        Initialize the camera object.
        :param device_index: Index of the video device
        """
        self.device_index = device_index
        self.cap = cv2.VideoCapture(device_index)

        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open camera at index {device_index}")

    def read_frame(self):
        """
        Read a frame from the camera
        :return: The captured frame, or None if reading failed
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        """
        Release the camera resource
        """
        self.cap.release()
