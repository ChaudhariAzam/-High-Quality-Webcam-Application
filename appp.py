import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
import time

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("High Quality Webcam Application")
        self.root.geometry("1200x800")
        
        # Webcam variables
        self.cap = None
        self.is_running = False
        self.photo_count = 0
        self.save_directory = "captured_photos"
        self.current_frame = None
        
        # Image processing variables
        self.brightness = 0
        self.contrast = 1.0
        self.sharpness = 1.0
        
        # Zoom variables
        self.zoom_factor = 1.0
        self.zoom_step = 0.1
        self.min_zoom = 1.0
        self.max_zoom = 3.0
        
        # Flip variables - FIXED: Initialize these variables
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # Create save directory
        self.create_save_directory()
        
        # Setup GUI
        self.setup_gui()
        
        # Test available cameras
        self.root.after(100, self.test_cameras)
        
    def create_save_directory(self):
        """Create directory for saving photos"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def test_cameras(self):
        """Test available cameras"""
        print("Testing available cameras...")
        available_cameras = []
        
        for i in range(4):  # Test cameras 0-3
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras.append(str(i))
                        print(f"Camera {i} found - {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                else:
                    print(f"Camera {i} not available")
            except Exception as e:
                print(f"Error testing camera {i}: {e}")
        
        # Update camera dropdown
        if available_cameras:
            self.camera_combo['values'] = available_cameras
            self.camera_var.set(available_cameras[0])
            self.status_label.config(text=f"Found {len(available_cameras)} camera(s) - Ready")
        else:
            self.status_label.config(text="No cameras found! Check connection")
            messagebox.showwarning("No Camera", 
                                "No cameras detected!\n\nPlease check:\n"
                                "• Camera is connected\n"
                                "• Drivers are installed\n"
                                "• No other app is using camera\n"
                                "• Camera permissions are granted")
    
    def setup_gui(self):
        """Setup the graphical user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Camera Controls", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Camera selection
        ttk.Label(control_frame, text="Select Camera:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.camera_var = tk.StringVar(value="0")
        self.camera_combo = ttk.Combobox(control_frame, textvariable=self.camera_var, 
                                       values=["0"], state="readonly", width=15)
        self.camera_combo.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(control_frame, text="Refresh Cameras", 
                  command=self.test_cameras).pack(fill=tk.X, pady=(0, 10))
        
        # Resolution selection
        ttk.Label(control_frame, text="Resolution:").pack(anchor=tk.W, pady=(0, 5))
        self.resolution_var = tk.StringVar(value="640x480")
        resolution_combo = ttk.Combobox(control_frame, textvariable=self.resolution_var,
                                       values=["640x480", "800x600", "1024x768", "1280x720", "1920x1080"],
                                       state="readonly", width=15)
        resolution_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Camera", command=self.start_camera)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Image adjustment controls
        self.setup_adjustment_controls(control_frame)
        
        # Zoom controls
        self.setup_zoom_controls(control_frame)
        
        # Effects controls
        self.setup_effects_controls(control_frame)
        
        # Status frame
        status_frame = ttk.LabelFrame(control_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Click 'Refresh Cameras'")
        self.status_label.pack(anchor=tk.W)
        
        self.photo_label = ttk.Label(status_frame, text="Photos: 0")
        self.photo_label.pack(anchor=tk.W)
        
        self.zoom_label = ttk.Label(status_frame, text=f"Zoom: {self.zoom_factor:.1f}x")
        self.zoom_label.pack(anchor=tk.W)
        
        # Right panel - Video feed
        video_frame = ttk.LabelFrame(main_frame, text="Live Feed", padding="10")
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.video_label = ttk.Label(video_frame, 
                                    text="Camera feed will appear here\n\n"
                                         "1. Click 'Refresh Cameras'\n"
                                         "2. Select your camera\n" 
                                         "3. Click 'Start Camera'", 
                                    background='black', 
                                    foreground='white', 
                                    justify=tk.CENTER,
                                    font=('Arial', 12))
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Capture button
        self.capture_btn = ttk.Button(video_frame, text="Capture Photo", 
                                     command=self.capture_photo, state=tk.DISABLED)
        self.capture_btn.pack(fill=tk.X, pady=(10, 0))
    
    def setup_adjustment_controls(self, parent):
        """Setup image adjustment controls"""
        adj_frame = ttk.LabelFrame(parent, text="Image Adjustments", padding="10")
        adj_frame.pack(fill=tk.X, pady=10)
        
        # Brightness
        ttk.Label(adj_frame, text="Brightness:").pack(anchor=tk.W)
        self.brightness_scale = ttk.Scale(adj_frame, from_=-100, to=100, 
                                        orient=tk.HORIZONTAL, command=self.update_brightness)
        self.brightness_scale.set(self.brightness)
        self.brightness_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Contrast
        ttk.Label(adj_frame, text="Contrast:").pack(anchor=tk.W)
        self.contrast_label = ttk.Label(adj_frame, text=f"Contrast: {self.contrast:.1f}")
        self.contrast_label.pack(anchor=tk.W)
        self.contrast_scale = ttk.Scale(adj_frame, from_=0.1, to=3.0, 
                                      orient=tk.HORIZONTAL, command=self.update_contrast)
        self.contrast_scale.set(self.contrast)
        self.contrast_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Sharpness
        ttk.Label(adj_frame, text="Sharpness:").pack(anchor=tk.W)
        self.sharpness_label = ttk.Label(adj_frame, text=f"Sharpness: {self.sharpness:.1f}")
        self.sharpness_label.pack(anchor=tk.W)
        self.sharpness_scale = ttk.Scale(adj_frame, from_=0.1, to=3.0, 
                                       orient=tk.HORIZONTAL, command=self.update_sharpness)
        self.sharpness_scale.set(self.sharpness)
        self.sharpness_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Reset button
        ttk.Button(adj_frame, text="Reset Adjustments", 
                  command=self.reset_adjustments).pack(fill=tk.X, pady=(5, 0))
    
    def setup_zoom_controls(self, parent):
        """Setup zoom controls"""
        zoom_frame = ttk.LabelFrame(parent, text="Zoom Controls", padding="10")
        zoom_frame.pack(fill=tk.X, pady=10)
        
        # Zoom scale
        self.zoom_label_ctrl = ttk.Label(zoom_frame, text=f"Zoom: {self.zoom_factor:.1f}x")
        self.zoom_label_ctrl.pack(anchor=tk.W)
        
        self.zoom_scale = ttk.Scale(zoom_frame, from_=self.min_zoom, to=self.max_zoom,
                                  orient=tk.HORIZONTAL, command=self.update_zoom)
        self.zoom_scale.set(self.zoom_factor)
        self.zoom_scale.pack(fill=tk.X, pady=(0, 5))
        
        # Zoom buttons
        zoom_btn_frame = ttk.Frame(zoom_frame)
        zoom_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(zoom_btn_frame, text="Zoom In +", 
                  command=lambda: self.change_zoom(self.zoom_step)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        ttk.Button(zoom_btn_frame, text="Zoom Out -", 
                  command=lambda: self.change_zoom(-self.zoom_step)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Reset zoom
        ttk.Button(zoom_frame, text="Reset Zoom", 
                  command=self.reset_zoom).pack(fill=tk.X, pady=(5, 0))
    
    def setup_effects_controls(self, parent):
        """Setup effects controls"""
        effects_frame = ttk.LabelFrame(parent, text="Effects", padding="10")
        effects_frame.pack(fill=tk.X, pady=10)
        
        # Flip controls
        flip_frame = ttk.Frame(effects_frame)
        flip_frame.pack(fill=tk.X, pady=5)
        
        self.flip_h_var = tk.BooleanVar(value=self.flip_horizontal)  # Initialize with current value
        ttk.Checkbutton(flip_frame, text="Flip Horizontal", 
                       variable=self.flip_h_var, command=self.update_flip).pack(side=tk.LEFT)
        
        self.flip_v_var = tk.BooleanVar(value=self.flip_vertical)  # Initialize with current value
        ttk.Checkbutton(flip_frame, text="Flip Vertical", 
                       variable=self.flip_v_var, command=self.update_flip).pack(side=tk.LEFT)
        
        # Grayscale
        self.grayscale_var = tk.BooleanVar()
        ttk.Checkbutton(effects_frame, text="Grayscale", 
                       variable=self.grayscale_var).pack(anchor=tk.W)
    
    def update_brightness(self, value):
        """Update brightness value"""
        self.brightness = int(float(value))
    
    def update_contrast(self, value):
        """Update contrast value"""
        self.contrast = float(value)
        self.contrast_label.config(text=f"Contrast: {self.contrast:.1f}")
    
    def update_sharpness(self, value):
        """Update sharpness value"""
        self.sharpness = float(value)
        self.sharpness_label.config(text=f"Sharpness: {self.sharpness:.1f}")
    
    def update_zoom(self, value):
        """Update zoom factor"""
        self.zoom_factor = float(value)
        self.zoom_label.config(text=f"Zoom: {self.zoom_factor:.1f}x")
        self.zoom_label_ctrl.config(text=f"Zoom: {self.zoom_factor:.1f}x")
    
    def change_zoom(self, delta):
        """Change zoom by delta amount"""
        new_zoom = self.zoom_factor + delta
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.zoom_factor = new_zoom
            self.zoom_scale.set(self.zoom_factor)
            self.zoom_label.config(text=f"Zoom: {self.zoom_factor:.1f}x")
            self.zoom_label_ctrl.config(text=f"Zoom: {self.zoom_factor:.1f}x")
    
    def reset_zoom(self):
        """Reset zoom to default"""
        self.zoom_factor = 1.0
        self.zoom_scale.set(self.zoom_factor)
        self.zoom_label.config(text=f"Zoom: {self.zoom_factor:.1f}x")
        self.zoom_label_ctrl.config(text=f"Zoom: {self.zoom_factor:.1f}x")
    
    def reset_adjustments(self):
        """Reset all image adjustments"""
        self.brightness = 0
        self.contrast = 1.0
        self.sharpness = 1.0
        
        self.brightness_scale.set(0)
        self.contrast_scale.set(1.0)
        self.sharpness_scale.set(1.0)
        
        self.contrast_label.config(text="Contrast: 1.0")
        self.sharpness_label.config(text="Sharpness: 1.0")
    
    def update_flip(self):
        """Update flip settings"""
        # FIXED: Now these variables are properly initialized
        self.flip_horizontal = self.flip_h_var.get()
        self.flip_vertical = self.flip_v_var.get()
    
    def apply_zoom(self, frame):
        """Apply zoom to frame"""
        if self.zoom_factor <= 1.0:
            return frame
        
        h, w = frame.shape[:2]
        
        # Calculate zoomed dimensions
        new_width = int(w / self.zoom_factor)
        new_height = int(h / self.zoom_factor)
        
        # Calculate center crop
        start_x = (w - new_width) // 2
        start_y = (h - new_height) // 2
        
        # Crop and resize back to original size
        cropped = frame[start_y:start_y + new_height, start_x:start_x + new_width]
        zoomed = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        
        return zoomed
    
    def apply_sharpness(self, frame):
        """Apply sharpness filter"""
        if self.sharpness == 1.0:
            return frame
        
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]]) * self.sharpness
        
        return cv2.filter2D(frame, -1, kernel)
    
    def start_camera(self):
        """Start the webcam"""
        try:
            camera_index = int(self.camera_var.get())
            
            # Try different backends for compatibility
            backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_V4L2, cv2.CAP_MSMF]
            
            for backend in backends:
                self.cap = cv2.VideoCapture(camera_index, backend)
                if self.cap.isOpened():
                    print(f"Camera opened with backend: {backend}")
                    break
            
            if not self.cap.isOpened():
                # Final attempt with default
                self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", 
                                   f"Cannot open camera {camera_index}\n\n"
                                   "Please check:\n"
                                   "• Camera is connected\n"
                                   "• No other app is using camera\n"
                                   "• Try different camera number")
                return
            
            # Set resolution
            try:
                width, height = map(int, self.resolution_var.get().split('x'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            except:
                print("Using default resolution")
            
            # Test frame capture
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                messagebox.showerror("Error", "Camera opened but cannot read frames")
                return
            
            # Get actual resolution
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.capture_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Camera {camera_index}: Running\n{actual_width}x{actual_height}")
            
            # Start video feed thread
            self.video_thread = threading.Thread(target=self.update_video_feed, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        """Stop the webcam"""
        self.is_running = False
        
        # Wait a bit for thread to finish
        time.sleep(0.2)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Camera: Stopped")
        self.video_label.config(image='', 
                               text="Camera stopped\n\nClick 'Start Camera' to restart")
    
    def process_frame(self, frame):
        """Apply all image processing effects"""
        processed = frame.copy()
        
        # Apply zoom first (before other processing for better quality)
        if self.zoom_factor > 1.0:
            processed = self.apply_zoom(processed)
        
        # Apply sharpness
        processed = self.apply_sharpness(processed)
        
        # Apply brightness and contrast
        processed = cv2.convertScaleAbs(processed, alpha=self.contrast, beta=self.brightness)
        
        # Apply grayscale
        if self.grayscale_var.get():
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        # Apply flip - FIXED: Now these variables are properly initialized
        if self.flip_horizontal or self.flip_vertical:
            flip_code = -1 if self.flip_horizontal and self.flip_vertical else (
                1 if self.flip_horizontal else 0
            )
            processed = cv2.flip(processed, flip_code)
        
        return processed
    
    def update_video_feed(self):
        """Update the video feed in the GUI"""
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            
            if ret:
                # Store current frame for capture
                self.current_frame = frame.copy()
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Convert to RGB for display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # Resize for display
                display_frame = self.resize_for_display(rgb_frame)
                
                # Convert to ImageTk format
                img = Image.fromarray(display_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update GUI in main thread
                self.root.after(0, self.update_video_label, imgtk)
            else:
                print("Failed to read frame from camera")
                break
            
            # Small delay
            cv2.waitKey(1)
    
    def resize_for_display(self, frame):
        """Resize frame for display while maintaining aspect ratio"""
        try:
            # Get label dimensions
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            
            if label_width > 10 and label_height > 10:
                h, w = frame.shape[:2]
                
                # Calculate scaling factor
                scale_w = label_width / w
                scale_h = label_height / h
                scale = min(scale_w, scale_h)
                
                if scale < 1:
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        except:
            pass
        
        return frame
    
    def update_video_label(self, imgtk):
        """Update the video label in the main thread"""
        try:
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        except:
            pass  # Ignore errors during window close
    
    def capture_photo(self):
        """Capture and save a high quality photo"""
        if not self.is_running or self.current_frame is None:
            messagebox.showwarning("Warning", "No camera feed available")
            return
        
        try:
            # Process the current frame with high quality settings
            processed_frame = self.process_frame(self.current_frame)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            filepath = os.path.join(self.save_directory, filename)
            
            # Save with high quality
            cv2.imwrite(filepath, processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.photo_count += 1
            self.photo_label.config(text=f"Photos: {self.photo_count}")
            
            messagebox.showinfo("Success", f"Photo saved as:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save photo: {str(e)}")
    
    def __del__(self):
        """Cleanup when application closes"""
        if self.cap:
            self.cap.release()

def main():
    """Main function to run the application"""
    try:
        # Check if OpenCV is working
        print("OpenCV version:", cv2.__version__)
        
        root = tk.Tk()
        app = WebcamApp(root)
        
        def on_closing():
            app.stop_camera()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")

if __name__ == "__main__":
    main()