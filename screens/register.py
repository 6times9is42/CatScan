import re
import sqlite3
from datetime import datetime
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from screens.shared import user_data

class RegisterScreen(Screen):
    def register_user(self):
        aadhaar = self.ids.aadhaar.text.strip()
        name = self.ids.name.text.strip()
        dob = self.ids.dob.text.strip()
        sex = self.ids.sex.text.strip()
        phone = self.ids.phone.text.strip()

        if not aadhaar.isdigit() or len(aadhaar) != 12:
            self.show_error("Invalid Aadhaar: 12 digits required.")
            return
        if not re.match(r"^[a-zA-Z ]+$", name):
            self.show_error("Invalid Name: Only letters and spaces allowed.")
            return
        try:
            parsed_dob = datetime.strptime(dob, "%d/%m/%Y")
            if parsed_dob > datetime.now():
                self.show_error("DOB cannot be in the future.")
                return
        except ValueError:
            self.show_error("Invalid DOB. Use DD/MM/YYYY format.")
            return
        if not phone.isdigit() or len(phone) != 10:
            self.show_error("Invalid Phone: Must be 10 digits.")
            return

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                      (aadhaar, name, dob, sex, phone))
            conn.commit()
        except sqlite3.IntegrityError:
            self.show_error("This Aadhaar is already registered. Please Sign In instead.")
            conn.close()
            return
        conn.close()

        user_data.update({
            "aadhaar": aadhaar,
            "name": name,
            "dob": dob,
            "sex": sex,
            "phone": phone,
        })

        self.manager.current = 'profile'

    def show_error(self, message):
        popup = Popup(title='Input Error',
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()
