import sqlite3
from kivy.uix.screenmanager import Screen
from screens.shared import user_data
from kivy.uix.screenmanager import Screen

class ProfileScreen(Screen):
    def on_enter(self):
        self.ids.aadhaar.text = user_data.get("aadhaar", "")
        self.ids.name.text = user_data.get("name", "")
        self.ids.dob.text = user_data.get("dob", "")
        self.ids.sex.text = user_data.get("sex", "")
        self.ids.phone.text = user_data.get("phone", "")
 
    def save_and_continue(self):
        # Get updated values from input fields
        aadhaar = self.ids.aadhaar.text.strip()
        name = self.ids.name.text.strip()
        dob = self.ids.dob.text.strip()
        sex = self.ids.sex.text.strip()
        phone = self.ids.phone.text.strip()

        # Update the database
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("""
            UPDATE users
            SET name = ?, dob = ?, sex = ?, phone = ?
            WHERE aadhaar = ?
        """, (name, dob, sex, phone, aadhaar))
        conn.commit()
        conn.close()

        # Update the shared user_data
        user_data.update({
            "aadhaar": aadhaar,
            "name": name,
            "dob": dob,
            "sex": sex,
            "phone": phone,
        })

        self.manager.current = 'eye_image'
    
    def go_to_database(self, instance):
        self.manager.current = 'database'