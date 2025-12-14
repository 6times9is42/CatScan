import sqlite3
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from screens.shared import user_data

class SignInScreen(Screen):
    def sign_in_user(self):
        aadhaar = self.ids.aadhaar.text.strip()
        phone = self.ids.phone.text.strip()

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE aadhaar=? AND phone=?", (aadhaar, phone))
        row = c.fetchone()
        conn.close()

        if row:
            user_data.update({
                "aadhaar": row[0],
                "name": row[1],
                "dob": row[2],
                "sex": row[3],
                "phone": row[4],
            })
            self.manager.current = 'profile'
        else:
            self.show_error("No user found with given Aadhaar and Phone.")

    def show_error(self, message):
        popup = Popup(title='Sign In Error',
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
