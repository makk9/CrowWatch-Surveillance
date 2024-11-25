import socket
import cv2
import numpy as np
import threading
from ultralytics import YOLO
import websockets
import asyncio


TCP_PORT = 65432
UDP_PORT = 65433
WEBSOCKET_PORT = 8765
HOST = "0.0.0.0"  # Listen on all interfaces

# Global variable for processed frames
processed_frame = None

def load_yolo():
    # Load YOLOv8-nano model
    model = YOLO("yolov8n.pt")  # YOLOv8-nano
    return model

def detect_objects_yolo(frame, model):
    # Perform detection
    results = model(frame, stream=True)
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            confidence = box.conf[0]  # Confidence score
            class_id = int(box.cls[0])  # Class ID
            label = model.names[class_id]  # Class label
            if confidence > 0.5:  # Confidence threshold
                detections.append((label, (x1, y1, x2 - x1, y2 - y1)))
    return detections

# Function to handle TCP metadata from clients
def handle_tcp_client(conn, addr):
    try:
        metadata = conn.recv(1024).decode()  # Receive metadata
        print(f"Metadata received from {addr}: {metadata}")
    except Exception as e:
        print(f"Error handling TCP client {addr}: {e}")
    finally:
        conn.close()

# Function to handle UDP frame streaming
def handle_udp_frames():
    global processed_frame  # Access the global processed frame
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    print(f"UDP Server listening on {HOST}:{UDP_PORT}")

    model = load_yolo()

    while True:
        try:
            data, addr = udp_socket.recvfrom(65535)  # Receive frame data
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            frame_count = 0
            detection_interval = 5
            if frame is not None:
                # Perform object detection
                #detections = detect_objects_yolo(frame, model)
                if frame_count % detection_interval == 0:
                    detections = detect_objects_yolo(frame, model)
                frame_count += 1
                for label, (x, y, w, h) in detections:
                    # Draw bounding box and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Update the processed frame
                processed_frame = frame
                    
                cv2.imshow(f"Live Feed from {addr}", frame)  # Display frame
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Error receiving frame from {addr}: {e}")
            break

    udp_socket.close()
    cv2.destroyAllWindows()

async def video_stream(websocket, path):
    """
    WebSocket handler to stream video frames to connected clients.
    """
    global processed_frame  # Access the latest processed frame
    print(f"WebSocket client connected: {websocket.remote_address}")

    try:
        while True:
            if processed_frame is not None:
                # Encode the processed frame to JPEG
                _, buffer = cv2.imencode('.jpg', processed_frame)
                await websocket.send(buffer.tobytes())
                print("Sending frame via WebSocket.")
                await asyncio.sleep(0.03)  # Adjust frame rate for streaming
    except Exception as e:
        print(f"Error in WebSocket video stream: {e}")
    finally:
        print(f"WebSocket client disconnected: {websocket.remote_address}")

if __name__ == "__main__":
    # Start TCP Server
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, TCP_PORT))
    tcp_socket.listen()
    print(f"TCP Server listening on {HOST}:{TCP_PORT}")

    # Start UDP handling in a separate thread
    udp_thread = threading.Thread(target=handle_udp_frames, daemon=True)
    udp_thread.start()

    async def main():
        # Start WebSocket Server
        websocket_server = await websockets.serve(video_stream, HOST, WEBSOCKET_PORT)
        print(f"WebSocket Server listening on ws://{HOST}:{WEBSOCKET_PORT}")

        try:
            # Handle incoming TCP connections
            while True:
                conn, addr = tcp_socket.accept()  # Accept TCP connections
                print(f"TCP connection established with {addr}")
                threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Shutting down server.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            tcp_socket.close()

    # Run the asyncio event loop
    asyncio.run(main())

    # # Start WebSocket Server
    # websocket_server = websockets.serve(video_stream, HOST, WEBSOCKET_PORT)
    # print(f"WebSocket Server listening on ws://{HOST}:{WEBSOCKET_PORT}")

    # # Run WebSocket server in asyncio loop
    # asyncio.get_event_loop().run_until_complete(websocket_server)

    # # Handle incoming TCP connections
    # try:
    #     while True:
    #         conn, addr = tcp_socket.accept()  # Accept TCP connections
    #         print(f"TCP connection established with {addr}")
    #         threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
    # except KeyboardInterrupt:
    #     print("Shutting down server.")
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     tcp_socket.close()

