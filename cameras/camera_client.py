import cv2
import socket
import json

# Server details
SERVER_IP = "96.230.30.54" # Server public IP
TCP_PORT = 65432
UDP_PORT = 65433

class CameraClient:
    def __init__(self, device_index):
        """
        Initialize the camera and networking sockets.
        """
        self.cap = cv2.VideoCapture(device_index)
        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open camera at index {device_index}")

        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self):
        """
        Establish a TCP connection to the server.
        """
        self.tcp_socket.connect((SERVER_IP, TCP_PORT))
        print(f"Connected to server at {SERVER_IP}:{TCP_PORT}")

    def send_metadata(self):
        """
        Send camera metadata to the server via TCP.
        """
        metadata = {
            "device_index": 0,
            "resolution": f"{int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
            "status": "active"
        }
        self.tcp_socket.sendall(json.dumps(metadata).encode())
        print("Metadata sent:", metadata)

    def stream_frames(self):
        """
        Capture frames from the webcam and send via UDP.
        """
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            
            # Resizing frames to reduce processing/transimssion overhead
            frame = cv2.resize(frame, (640, 480))
            #frame = cv2.resize(frame, (320, 240))
            # Encode frame as JPEG
            #_, buffer = cv2.imencode('.jpg', frame)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])  # Reduce quality (50)

            # Send frame over UDP
            self.udp_socket.sendto(buffer.tobytes(), (SERVER_IP, UDP_PORT))
            print("Frame sent.")

    def release(self):
        """
        Release the camera and close sockets.
        """
        self.cap.release()
        self.tcp_socket.close()
        self.udp_socket.close()
        print("Resources released.")

if __name__ == "__main__":
    client = CameraClient(0)
    try:
        client.connect()
        client.send_metadata()
        client.stream_frames()
    finally:
        client.release()
