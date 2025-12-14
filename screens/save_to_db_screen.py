# save_to_db_screen.py
from kivy.uix.screenmanager import Screen
import sqlite3
from datetime import datetime
from screens.shared import user_data
import os
import shutil


class SaveToDbScreen(Screen):
    def on_pre_enter(self):
        pred = user_data.get('prediction', 'Processing...')
        self.ids.prediction.text = f"Prediction: {pred}"
        self.ids.notes.text = ""

        # Set the image source from result screen
        result_screen = self.manager.get_screen('result')
        if hasattr(result_screen.ids, 'result_image') and result_screen.ids.result_image.source:
            self.ids.save_image.source = result_screen.ids.result_image.source
            self.ids.save_image.reload()

    def get_current_image_path(self):
        # Get the current image from the workflow
        result_screen = self.manager.get_screen('result')
        if hasattr(result_screen.ids, 'result_image') and result_screen.ids.result_image.source:
            return result_screen.ids.result_image.source

        # Fallback to view_image screen
        view_image_screen = self.manager.get_screen('view_image')
        if hasattr(view_image_screen.ids, 'image') and view_image_screen.ids.image.source:
            return view_image_screen.ids.image.source

        return None

    def save_to_db(self):
        notes = self.ids.notes.text
        prediction = self.ids.prediction.text.replace("Prediction: ", "")
        date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        aadhaar = user_data.get("aadhaar", "")

        # Paths from UI / stored state
        current_image_path = self.get_current_image_path()
        original_filename = user_data.get('original_image_path', None)

        # Normalize original_filename to absolute if present
        if original_filename:
            try:
                original_filename = os.path.abspath(original_filename)
            except Exception:
                pass

        # Decide which file to copy into saved_images:
        # prefer the currently-displayed image (might be edited/temp),
        # otherwise fall back to original file if it exists.
        source_to_copy = None
        if current_image_path and os.path.exists(current_image_path):
            source_to_copy = current_image_path
        elif original_filename and os.path.exists(original_filename):
            source_to_copy = original_filename

        saved_abs_path = None
        if source_to_copy:
            image_folder = os.path.join(os.getcwd(), "saved_images")
            os.makedirs(image_folder, exist_ok=True)

            # preserve extension
            ext = os.path.splitext(source_to_copy)[1] or os.path.splitext(original_filename or "")[1] or ".jpg"
            # sanitize aadhaar/date for filename (optional)
            safe_aadhaar = str(aadhaar).replace(" ", "_")
            safe_date = date.replace(":", "-").replace(" ", "_")
            image_filename = f"{safe_aadhaar}_{safe_date}{ext}"
            saved_image_path = os.path.join(image_folder, image_filename)

            try:
                shutil.copy2(source_to_copy, saved_image_path)
                # store absolute path in DB (as requested)
                saved_abs_path = os.path.abspath(saved_image_path)
            except Exception as e:
                print(f"Error saving image: {e}")
                # fallback: try to record the absolute source path if available
                saved_abs_path = os.path.abspath(source_to_copy) if source_to_copy else None
        else:
            saved_abs_path = None

        # Use absolute original filename if available (else None)
        orig_for_db = os.path.abspath(original_filename) if original_filename else None

        # Save to database
        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO visits (aadhaar, date, prediction, image_path, notes, original_filename)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (aadhaar, date, prediction, saved_abs_path, notes, orig_for_db))
            conn.commit()
        except Exception as e:
            print(f"Database error while saving visit: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

        print(f"Visit saved successfully for {aadhaar}")
        self.manager.current = 'profile'
