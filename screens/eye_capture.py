# gallery_upload_screen.py
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
# Platform-specific picker
if platform == 'android' or platform == 'ios':
    from plyer import filechooser
else:
    import tkinter as tk
    from tkinter import filedialog


class GalleryUploadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_path = None

    def on_enter(self):
        """Build simple interface for native file picker"""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        pick_btn = Button(
            text="Select Image from Device",
            size_hint=(None, None),
            size=(250, 60),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        pick_btn.bind(on_press=self.open_file_picker)
        layout.add_widget(pick_btn)

        back_btn = Button(
            text="← Back",
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.5, 0.8, 1),
            font_size='18sp',
            bold=True
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def open_file_picker(self, instance):
        """Open native file picker"""
        if platform in ('android', 'ios'):
            filechooser.open_file(on_selection=self.on_file_selected)
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
            )
            if file_path:
                self.on_file_selected([file_path])

    def on_file_selected(self, selection):
        """Handle file selection"""
        if selection:
            self.selected_path = selection[0]
            view_screen = self.manager.get_screen('view_image')
            view_screen.ids.image.source = self.selected_path
            view_screen.ids.image.reload()
            self.manager.current = 'view_image'

    def go_back(self):
        self.manager.current = 'eye_image'

# camera_capture_screen.py (can be in the same file or separate)



# Mobile camera API
if platform in ('android', 'ios'):
    from plyer import camera
else:
    # Desktop: fallback with OpenCV
    import cv2
    import os
    from datetime import datetime

class CameraCaptureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.captured_path = None

    def on_enter(self):
        """Build interface"""
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        capture_btn = Button(
            text="Take Picture",
            size_hint=(None, None),
            size=(250, 60),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        capture_btn.bind(on_press=self.capture_image)
        layout.add_widget(capture_btn)

        back_btn = Button(
            text="← Back",
            size_hint=(None, None),
            size=(150, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.8, 0.8, 0.8, 1),
            color=(0.2, 0.5, 0.8, 1),
            font_size='18sp',
            bold=True
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def capture_image(self, instance):
        """Open camera and capture image"""
        if platform in ('android', 'ios'):
            filename = "captured_image.jpg"
            camera.take_picture(filename=filename, on_complete=self.on_picture_taken)
        else:
            # Desktop fallback using OpenCV
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Cannot access camera")
                return

            ret, frame = cap.read()
            if ret:
                filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                self.on_picture_taken(filename)
            cap.release()
            cv2.destroyAllWindows()

    def on_picture_taken(self, filepath):
        """Handle captured image"""
        if filepath:
            self.captured_path = filepath
            view_screen = self.manager.get_screen('view_image')
            view_screen.ids.image.source = self.captured_path
            view_screen.ids.image.reload()
            self.manager.current = 'view_image'

    def go_back(self):
        self.manager.current = 'gallery_upload'
