from email.mime import text
from screens.shared import user_data
import sqlite3
import functools
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

class DatabaseScreen(Screen):
    def on_pre_enter(self):
        self.ids.visits_box.clear_widgets()
        visits = self.get_visits()
        if visits:
            for visit in visits:
                btn = Button(
                    text=visit['visit_date'],
                    size_hint_y= None,
                    height= 30,
                    background_normal= '',
                    background_color= (0.8, 0.8, 0.8, 1),
                    color= (0.2, 0.5, 0.8, 1),
                    font_size= '14sp',
                    bold= True,
                    on_release=lambda inst, vid=visit['visit_id']: self.open_visit(vid)
                )
                self.ids.visits_box.add_widget(btn)
        else:
            self.ids.visits_box.add_widget(Label(
                text="No previous visits",
                font_size='18sp',
                color=(0.2, 0.3, 0.4, 1),
                size_hint_y=None,
                height=220
            ))

    def get_visits(self):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        aadhaar = user_data.get('aadhaar', '')
        if aadhaar:
            c.execute("""
                SELECT id, date FROM visits
                WHERE aadhaar = ? AND image_path LIKE '%' || ? || '%'
                ORDER BY date DESC
            """, (aadhaar, aadhaar))
            rows = c.fetchall()
        else:
            rows = []
        conn.close()
        return [{'visit_id': row[0], 'visit_date': row[1]} for row in rows]


    def open_visit(self, visit_id):
        detail_screen = self.manager.get_screen('visit_detail')
        detail_screen.load_visit(visit_id)
        self.manager.current = 'visit_detail'

    def go_to_eye_image(self, instance):
        self.manager.current = 'eye_image'