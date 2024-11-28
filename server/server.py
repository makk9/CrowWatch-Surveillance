import socket
import cv2
import numpy as np
import threading
from ultralytics import YOLO
import websockets
import asyncio
import logging
from threading import Lock

frame_lock = Lock()


# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

TCP_PORT = 65432
UDP_PORT = 65433
WEBSOCKET_PORT = 8765
HOST = "0.0.0.0"  # Listen on all interfaces

# Global variable for processed frames
processed_frame = None

async def video_stream(websocket, path=None):
    """
    WebSocket handler to stream video frames to connected clients.
    """
    global processed_frame  # Access the latest processed frame
    logging.info(f"WebSocket client connected: {websocket.remote_address}")

    try:
        while True:
            with frame_lock:
                if processed_frame is not None:
                    # Encode the processed frame to JPEG
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    await websocket.send(buffer.tobytes())
                    #logging.info("Sending frame via WebSocket.")
                    await asyncio.sleep(0.03)  # Adjust frame rate for streaming
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"WebSocket client disconnected: {websocket.remote_address}")
    except Exception as e:
        logging.error(f"Error in WebSocket video stream: {e}")

async def start_websocket_server():
    """
    Start WebSocket server
    """
    server = await websockets.serve(
        video_stream, 
        HOST, 
        WEBSOCKET_PORT,
        # ping_interval=20,  # Send ping every 20 seconds
        # ping_timeout=20    # Timeout after 20 seconds if no pong received
    )
    logging.info(f"WebSocket Server listening on ws://{HOST}:{WEBSOCKET_PORT}")
    await server.wait_closed()

def start_tcp_server():
    """
    Start TCP server in a separate thread
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, TCP_PORT))
    tcp_socket.listen()
    logging.info(f"TCP Server listening on {HOST}:{TCP_PORT}")

    try:
        while True:
            conn, addr = tcp_socket.accept()  # Accept TCP connections
            logging.info(f"TCP connection established with {addr}")
            threading.Thread(
                target=handle_tcp_client, 
                args=(conn, addr), 
                daemon=True
            ).start()
    except Exception as e:
        logging.error(f"TCP Server error: {e}")
    finally:
        tcp_socket.close()

def handle_udp_frames():
    """
    Handle UDP frame streaming
    """
    global processed_frame  # Access the global processed frame
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))
    logging.info(f"UDP Server listening on {HOST}:{UDP_PORT}")

    model = YOLO("yolov8n.pt")  # Load YOLO model

    while True:
        try:
            data, addr = udp_socket.recvfrom(65535)  # Receive frame data
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            frame_count = 0
            detection_interval = 20
            if frame is not None:
                # Perform object detection
                detections = detect_objects_yolo(frame, model)
                if frame_count % detection_interval == 0:
                    detections = detect_objects_yolo(frame, model)
                frame_count += 1
                
                for label, (x, y, w, h) in detections:
                    # Draw bounding box and label
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Update the processed frame
                with frame_lock:
                    processed_frame = frame
                    
                # cv2.imshow(f"Live Feed from {addr}", frame)  # Display frame
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
        except Exception as e:
            logging.error(f"Error receiving frame from UDP: {e}")
            break

    udp_socket.close()
    cv2.destroyAllWindows()

def detect_objects_yolo(frame, model):
    """
    Perform object detection using YOLO
    """
    resized_frame = cv2.resize(frame, (320, 320))  # Resize to 320x320 (YOLO-friendly)
    results = model(resized_frame, stream=True, imgsz=320)
    #results = model(frame, stream=True)
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

def handle_tcp_client(conn, addr):
    """
    Handle individual TCP client connections
    """
    try:
        metadata = conn.recv(1024).decode()  # Receive metadata
        logging.info(f"Metadata received from {addr}: {metadata}")
    except Exception as e:
        logging.error(f"Error handling TCP client {addr}: {e}")
    finally:
        conn.close()

def main():
    """
    Main function to start all server components
    """
    # Start UDP handling in a separate thread
    udp_thread = threading.Thread(target=handle_udp_frames, daemon=True)
    udp_thread.start()

    # Start TCP server in a separate thread
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Run WebSocket server
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_websocket_server())
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down server.")
    except Exception as e:
        logging.error(f"Server error: {e}")

if __name__ == "__main__":
    main()