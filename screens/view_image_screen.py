from kivy.uix.screenmanager import Screen

class ViewImageScreen(Screen):
    def go_to_image_edit(self):
        self.manager.current = 'image_edit'
