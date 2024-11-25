### **Crow's Watch**:

**Real-Time Camera Surveillance and Object Tracking System**

### **Objective**:

Build a system that integrates multiple live camera feeds into a modular surveillance platform, processes real-time video data to detect and track "airborne threats" (e.g., birds), and visualizes this information through a simple UI control dashboard.

### **Core Features**:

1. **Camera Integration**:
    - Handle two live camera feeds, one of which will simulate IR imaging using image processing filters.
    - Integrate with one live server.
    - Display real-time video streams and data to a "control center" dashboard.
2. **Object Detection & Tracking**:
    - Use existing object detection models (YOLOv8-nano) to detect and track birds in real-time.
    - Highlight detected objects and visualize their paths on the video feed.
3. **"Control Center" UI Dashboard**:
    - Display video feeds (standard and simulated IR).
    - View "threats"
5. **Networking with TCP, UDP, and Port Forwarding**:
    - **TCP**: Used for reliable transmission of metadata (e.g., toggling cameras on/off, changing settings).
    - **UDP**: Used for real-time video stream transmission.
    - **Port Forwarding**: Simulated transmitting video streams on different networks to a central server using specific ports.
6. **NixOS Configuration**:
    - Create a `flake.nix` to package the project and environment for easy replication on other systems.

### **Environment**:

- **OS**: Linux
- **Backend**: Python, OpenCV, pre-trained detection model (YOLO).
- **Frontend**: React
- **Networking**: TCP and UDP protocols with port forwarding.

### **Stretch Goals**:
- Mesh Networking - multi-node network where multiple clients relay data to a central server
- Prioritize Data - send metadata (TCP) and frame data (UDP) with a priority-based system.
- Be able to classify and discern between different types of birds — ex: Crows could be allies, Blue jays could be threats.
- More secure form of data transmission.

### **Progress So Far(updated: 11/25/2024)**:
    - Integrated a live camera feed running on a different network into system.
    - Added simulated IR imaging to one feed using OpenCV filters to replicate thermal imaging effects.
    - Developed a modular Camera class to handle different functionalities like resolution adjustments and IR simulation.
    - Integrated YOLOv8-nano for lightweight, efficient object detection.
        - Successfully tested the model, displaying bounding boxes and labels for detected objects on live video streams.
    - UDP Streaming:
        - Configured a client-server architecture to stream live video frames from a client device to the server using UDP.
        -Handled frame encoding and decoding for efficient transmission.
    - TCP Metadata Handling:
        - Implemented TCP for transmitting control signals and metadata between the client and server.
    - Port Forwarding:
        - Configured the system to handle real-world network setups by testing and implementing port forwarding.
    - Set up a WebSocket server to stream processed video frames to a React-based user interface.
    - Very basic "Control Center" interface that just has live video feed as of now.
