import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

class VisitDetailScreen(Screen):
    def load_visit(self, visit_id):
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT image_path, prediction, notes FROM visits WHERE id=?", (visit_id,))
        row = c.fetchone()
        conn.close()
        if row:
            image_path, prediction, notes = row
            self.ids.visit_image.source = image_path
            self.ids.visit_prediction.text = prediction
            self.ids.visit_notes.text = notes
        else:
            self.ids.visit_image.source = ""
            self.ids.visit_prediction.text = "No data found."
            self.ids.visit_notes.text = "No data found."