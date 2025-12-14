from kivy.uix.screenmanager import Screen

class EyeImageScreen(Screen):
    def goto_camera(self):
        self.manager.current = 'camera_capture'

    def goto_gallery(self):
        self.manager.current = 'gallery_upload'