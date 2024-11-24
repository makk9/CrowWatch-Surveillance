from cameras.camera import Camera
from cameras.ir_camera import IRCamera
import cv2

# Initialize cameras
#standard_camera = Camera(0) 
ir_camera = IRCamera(0)

try:
    while True:
        # Capture frames
        #standard_frame = standard_camera.read_frame()
        ir_frame = ir_camera.read_frame()

        # if standard_frame is None or ir_frame is None:
        #     print("Error: Could not read from one or both cameras.")
        #     break

        # Display feeds
        #cv2.imshow("Standard Camera", standard_frame)
        cv2.imshow("Simulated IR Camera", ir_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Release resources
    #standard_camera.release()
    ir_camera.release()
    cv2.destroyAllWindows()

