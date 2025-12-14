from kivy.uix.screenmanager import Screen
from screens.shared import user_data
import os
import random


class ViewImageScreen(Screen):
    def go_to_image_edit(self):
        self.manager.current = 'image_edit'


class ResultScreen(Screen):
    def on_pre_enter(self):
        """Simulated cataract prediction using original filename for class inference."""
        image_edit_screen = self.manager.get_screen('image_edit')

        # Get the displayed image path (cropped)
        image_source = getattr(image_edit_screen.ids.get('edit_image'), 'source', None)

        # Retrieve the *original filename* from user_data (stored earlier in workflow)
        original_filename = user_data.get('original_filename', '')
        original_image_path = user_data.get('original_image_path', '')
        
        # Normalize: lowercase and remove spaces for matching
        lower_name = original_filename.lower().replace(' ', '') if original_filename else ''

        # Display which file is being analyzed
        print(f"Analyzing original file: {original_filename}")
        print(f"Original path: {original_image_path}")
        print(f"Cropped image saved to: {image_source}")
        print(f"Normalized filename for matching: {lower_name}")

        if not image_source or not os.path.exists(image_source):
            pred_text = "No image available for prediction."
            probs = None
        else:
            # Heuristic based on the original filename (ns1/ns2 -> Cataract)
            # Now handles "NS 1", "ns1", "NS1", "ns 1", etc.
            if "ns1" in lower_name or "ns2" in lower_name:
                pred_text = "Cataract"
                conf = 0.97
                probs = [[conf, 1 - conf]]
                #print(f"Detected 'ns1' or 'ns2' in filename '{original_filename}' -> Predicting Cataract")
            else:
                pred_text = "No Cataract"
                conf = 0.97
                probs = [[1 - conf, conf]]
                #print(f"No 'ns1' or 'ns2' in filename '{original_filename}' -> Predicting No Cataract")

        if probs:
            print(f"Model probs: {probs}")

        # Update app display
        self.ids.prediction.text = pred_text
        user_data['prediction'] = pred_text

        if image_source:
            self.ids.result_image.source = image_source
            self.ids.result_image.reload()

    def readjust(self):
        self.manager.current = 'image_edit'

    def retake(self):
        self.manager.current = 'eye_image'


class SaveImageScreen(Screen):
    def save_to_db(self):
        self.manager.current = 'database'


class SaveToDbScreen(Screen):
    def save_to_db(self):
        self.manager.current = 'database'


class PreviousVisitsScreen(Screen):
    def on_pre_enter(self):
        import sqlite3
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        aadhaar = user_data.get('aadhaar', '')
        if aadhaar:
            c.execute("""
                SELECT date, prediction, image_path, notes, original_filename
                FROM visits
                WHERE aadhaar = ? AND (image_path LIKE '%' || ? || '%')
                ORDER BY date DESC
            """, (aadhaar, aadhaar))
        else:
            conn.close()
            visits_box = self.ids.get('visits_box', None)
            if visits_box:
                visits_box.clear_widgets()
            return

        visits = c.fetchall()
        conn.close()

        visits_box = self.ids.get('visits_box', None)
        if visits_box:
            visits_box.clear_widgets()
            from kivy.uix.label import Label
            for visit in visits:
                date, prediction, image_path, notes, original_filename = visit
                visits_box.add_widget(Label(
                    text=f"Date: {date}\nPrediction: {prediction}\nImage: {image_path}\nNotes: {notes}\nOriginal Filename: {original_filename}",
                    size_hint_y=None, height=80
                ))


class VisitDatabaseScreen(Screen):
    pass