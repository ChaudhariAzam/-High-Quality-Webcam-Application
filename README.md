# 📷 High Quality Webcam Application

A powerful Python + OpenCV + Tkinter based desktop webcam application
with:

-   🎥 Live camera preview
-   🔎 Dynamic camera detection
-   🎛 Brightness / Contrast / Sharpness control
-   🔍 Smooth digital zoom (1x -- 3x)
-   🔄 Flip (Horizontal & Vertical)
-   ⚫ Grayscale effect
-   📸 High-quality photo capture (95% JPEG)
-   🧠 Multi-backend camera compatibility
-   🗂 Auto timestamp photo saving

------------------------------------------------------------------------

## 🚀 Features

### 🎥 Smart Camera Detection

-   Automatically scans camera indexes (0--3)
-   Displays available cameras
-   Handles driver conflicts
-   Multiple backend fallback support:
    -   CAP_ANY
    -   CAP_DSHOW
    -   CAP_V4L2
    -   CAP_MSMF

------------------------------------------------------------------------

### 🎛 Image Processing Controls

  Feature           Description
  ----------------- -----------------------------
  Brightness        Adjust lighting dynamically
  Contrast          Enhance image intensity
  Sharpness         Apply edge-enhancing kernel
  Zoom              Center-based digital zoom
  Flip Horizontal   Mirror image
  Flip Vertical     Invert image
  Grayscale         Convert to black & white

------------------------------------------------------------------------

## 🧠 Image Processing Pipeline

Each frame goes through:

1.  Zoom (center crop + resize)
2.  Sharpness filter (custom kernel)
3.  Brightness & contrast scaling
4.  Optional grayscale conversion
5.  Optional flip transformation
6.  Display on Tkinter GUI

------------------------------------------------------------------------

## 📂 Project Structure

webcam_app/ │ ├── webcam_app.py ├── captured_photos/ └── README.md

------------------------------------------------------------------------

## ⚙️ Requirements

-   Python 3.8+
-   OpenCV
-   Pillow
-   NumPy
-   Tkinter (comes with Python)

Install dependencies:

pip install opencv-python pillow numpy

------------------------------------------------------------------------

## ▶️ How to Run

python webcam_app.py

------------------------------------------------------------------------

## 📸 Photo Capture

When you click Capture Photo:

-   Uses latest full-resolution frame
-   Applies current processing settings
-   Saves as:

photo_YYYYMMDD_HHMMSS.jpg

-   JPEG Quality: 95%
-   Stored in: captured_photos/

------------------------------------------------------------------------

## 🛠 Error Handling

The application handles:

-   Camera not found
-   Camera busy
-   Frame read failure
-   Resolution not supported
-   Safe shutdown on window close

------------------------------------------------------------------------

## 📈 Future Improvements

-   Video recording feature
-   Face detection integration
-   Snapshot preview gallery
-   FPS counter
-   AI-based auto enhancement

------------------------------------------------------------------------

© 2026 High Quality Webcam Application
