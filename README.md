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
