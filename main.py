import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder

# Import all screen classes
from screens.first import FirstScreen
from screens.register import RegisterScreen
from screens.signin import SignInScreen
from screens.profile import ProfileScreen
from screens.eye_image_screen import EyeImageScreen
from screens.eye_capture import GalleryUploadScreen
from screens.eye_capture import CameraCaptureScreen
from screens.view_image_screen import ViewImageScreen
from screens.image_edit import ImageEditScreen
from screens.others import ResultScreen
from screens.save_to_db_screen import SaveToDbScreen
from screens.database import DatabaseScreen
from screens.visit_detail import VisitDetailScreen
Window.clearcolor = (1, 1, 1, 1)

class EyeApp(App):
    def build(self):
        # Initialize database
        self.init_database()
        
        # Load KV file
        Builder.load_file("eye.kv")
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(FirstScreen(name='first'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(SignInScreen(name='signin'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(EyeImageScreen(name='eye_image'))
        sm.add_widget(CameraCaptureScreen(name='camera_capture'))
        sm.add_widget(GalleryUploadScreen(name='gallery_upload'))
        sm.add_widget(ViewImageScreen(name='view_image'))
        sm.add_widget(ImageEditScreen(name='image_edit'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(SaveToDbScreen(name='save_to_db'))
        sm.add_widget(DatabaseScreen(name='database'))
        sm.add_widget(VisitDetailScreen(name='visit_detail'))
        sm.current = 'first'
        return sm

    def init_database(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                aadhaar TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                sex TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        # Create visits table
        c.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aadhaar TEXT NOT NULL,
                date TEXT NOT NULL,
                prediction TEXT NOT NULL,
                image_path TEXT,
                notes TEXT,
                FOREIGN KEY (aadhaar) REFERENCES users (aadhaar)
            )
        ''')
        
        conn.commit()
        conn.close()

if __name__ == '__main__':
    EyeApp().run()