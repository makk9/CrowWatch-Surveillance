from cameras.camera import Camera
import cv2
import numpy as np

class IRCamera(Camera):
    def __init__(self, device_index):
        super().__init__(device_index)

    def read_frame(self, advanced=True):
        """
        Read a frame and apply a simple IR simulation effect
        :return: The simulated IR frame
        """
        frame = super().read_frame()
        if frame is None:
            return None
        
        if not advanced:
            # Apply IR simulation
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ir_frame = cv2.applyColorMap(gray_frame, cv2.COLORMAP_JET)
        else:
            # Apply advanced IR simulation
            ir_frame = self.simulate_ir_effect_advanced(frame)
        return ir_frame

    def simulate_ir_effect_advanced(self, frame, temp_range=(20, 35), noise_level=0.1, blur_amount=3):
        """
        Simulate IR thermal imaging with customizable parameters
        
        Args:
            frame: Input BGR frame
            temp_range: Tuple of (min_temp, max_temp) in Celsius for temperature simulation
            noise_level: Amount of thermal noise to simulate (0.0 to 1.0)
            blur_amount: Amount of blur to simulate IR sensor characteristics
        
        Returns:
            Simulated IR frame
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to simulate IR sensor characteristics
        blurred = cv2.GaussianBlur(gray, (blur_amount, blur_amount), 0)
        
        # Enhance contrast to simulate temperature differences
        # This helps distinguish "hot" and "cold" areas better
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)
        
        # Add random noise to simulate thermal sensor noise
        noise = np.random.normal(0, noise_level * 255, enhanced.shape).astype(np.uint8)
        noisy = cv2.add(enhanced, noise)
        
        # Apply custom temperature mapping
        # Map pixel values to simulated temperature range
        temp_mapped = np.interp(noisy, 
                            (0, 255), 
                            temp_range)
        
        # Normalize back to 0-255 range for colormapping
        normalized = cv2.normalize(temp_mapped, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply IR-like colormap
        # COLORMAP_JET is common for thermal imaging, but you can experiment with others:
        # - COLORMAP_INFERNO: More natural thermal look
        # - COLORMAP_HOT: Traditional thermal camera look
        ir_frame = cv2.applyColorMap(normalized, cv2.COLORMAP_INFERNO)
        
        # Optionally add temperature scale overlay
        height, width = ir_frame.shape[:2]
        scale_width = 30
        scale = np.linspace(255, 0, height).astype(np.uint8)
        scale = np.tile(scale, (scale_width, 1)).T
        scale_colored = cv2.applyColorMap(scale, cv2.COLORMAP_INFERNO)
        
        # Add temperature values on the scale
        temp_scale = ir_frame.copy()
        temp_scale = np.hstack((temp_scale, scale_colored))
        
        for i, temp in enumerate(np.linspace(temp_range[1], temp_range[0], 5)):
            y_pos = int(i * (height-1) / 4)
            cv2.putText(temp_scale, 
                        f'{temp:.1f}°C', 
                        (width + scale_width + 5, y_pos + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.4, 
                        (255, 255, 255), 
                        1)
        
        return temp_scale
