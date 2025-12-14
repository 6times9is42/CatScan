# image_edit.py
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse, InstructionGroup
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from PIL import Image as PILImage, ImageOps, ImageDraw
import re
import os
import tempfile
import uuid

# small shared state storage (must exist in your project)
from screens.shared import user_data


class SimpleCropOverlay(Widget):
    """
    Crop overlay with a single draggable, resizable circle.
    - Circle can be dragged around
    - Circle radius can be resized by touching near border
    - Clean border with subtle overlay
    """
    border_color = ListProperty([0.2, 0.5, 0.8, 1])      # Blue border
    overlay_color = ListProperty([0, 0, 0, 0.3])         # Light dark overlay
    crop_size = NumericProperty(120)                     # Initial diameter

    def __init__(self, image_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.image_widget = image_widget
        self.dragging = False
        self.resizing = False
        self.drag_offset = (0, 0)
        self.handle_radius = 20  # tolerance for resizing near border

        self._overlay_instructions = InstructionGroup()
        self.canvas.add(self._overlay_instructions)

        # Circle diameter and position
        self.crop_d = self.crop_size
        self.crop_x = 0
        self.crop_y = 0

        # Bind to updates
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def set_image_widget(self, image_widget):
        self.image_widget = image_widget
        self.update_graphics()

    def get_image_bounds(self):
        if not self.image_widget or not self.image_widget.texture:
            return (0, 0, 100, 100) if not self.image_widget else self.image_widget.pos + self.image_widget.size

        tex_w, tex_h = self.image_widget.texture_size
        widget_w, widget_h = self.image_widget.size
        widget_x, widget_y = self.image_widget.pos

        if tex_w > 0 and tex_h > 0:
            scale = min(widget_w / tex_w, widget_h / tex_h)
            disp_w = tex_w * scale
            disp_h = tex_h * scale
            disp_x = widget_x + (widget_w - disp_w) / 2.0
            disp_y = widget_y + (widget_h - disp_h) / 2.0
            return (disp_x, disp_y, disp_w, disp_h)
        else:
            return (widget_x, widget_y, widget_w, widget_h)

    def center_crop(self):
        if not self.image_widget:
            return
        img_x, img_y, img_w, img_h = self.get_image_bounds()
        self.crop_x = img_x + (img_w - self.crop_d) / 2
        self.crop_y = img_y + (img_h - self.crop_d) / 2
        self._clamp_to_image()
        self.update_graphics()

    def update_graphics(self, *args):
        self._overlay_instructions.clear()
        if not self.image_widget:
            return

        img_x, img_y, img_w, img_h = self.get_image_bounds()
        cx, cy = self.crop_x + self.crop_d/2, self.crop_y + self.crop_d/2

        # Dark overlay on image
        self._overlay_instructions.add(Color(*self.overlay_color))
        self._overlay_instructions.add(Rectangle(pos=(img_x, img_y), size=(img_w, img_h)))

        # Transparent circle cutout (visual only — Kivy canvas doesn't truly subtract)
        self._overlay_instructions.add(Color(1, 1, 1, 0))
        self._overlay_instructions.add(Ellipse(pos=(self.crop_x, self.crop_y), size=(self.crop_d, self.crop_d)))

        # Circle border
        self._overlay_instructions.add(Color(*self.border_color))
        self._overlay_instructions.add(Line(circle=(cx, cy, self.crop_d/2), width=2))


    def on_touch_down(self, touch):
        cx, cy = self.crop_x + self.crop_d/2, self.crop_y + self.crop_d/2
        r = self.crop_d/2
        dist = ((touch.x - cx)**2 + (touch.y - cy)**2)**0.5

        # Resize mode if near border
        if abs(dist - r) <= self.handle_radius:
            self.resizing = True
            touch.grab(self)
            return True

        # Drag mode if inside center handle (small center zone)
        if ((touch.x - cx)**2 + (touch.y - cy)**2)**0.5 <= 10:
            self.dragging = True
            self.drag_offset = (touch.x - cx, touch.y - cy)
            touch.grab(self)
            return True

        # Drag mode if inside circle
        if dist < r:
            self.dragging = True
            self.drag_offset = (touch.x - self.crop_x, touch.y - self.crop_y)
            touch.grab(self)
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current != self:
            return False

        cx, cy = self.crop_x + self.crop_d/2, self.crop_y + self.crop_d/2

        if self.dragging:
            # If dragging from center handle, use offset from center
            cx, cy = self.crop_x + self.crop_d/2, self.crop_y + self.crop_d/2
            if ((touch.x - cx)**2 + (touch.y - cy)**2)**0.5 <= 10:
                new_cx = touch.x - self.drag_offset[0]
                new_cy = touch.y - self.drag_offset[1]
                self.crop_x = new_cx - self.crop_d/2
                self.crop_y = new_cy - self.crop_d/2
            else:
                new_x = touch.x - self.drag_offset[0]
                new_y = touch.y - self.drag_offset[1]
                self.crop_x = new_x
                self.crop_y = new_y
            self._clamp_to_image()

        elif self.resizing:
            new_r = ((touch.x - cx)**2 + (touch.y - cy)**2)**0.5
            self.crop_d = max(40, 2 * new_r)  # enforce minimum diameter
            self.crop_x = cx - self.crop_d/2
            self.crop_y = cy - self.crop_d/2
            self._clamp_to_image()

        self.update_graphics()
        return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.dragging = False
            self.resizing = False
            touch.ungrab(self)
            return True
        return False

    def _clamp_to_image(self):
        if not self.image_widget:
            return
        img_x, img_y, img_w, img_h = self.get_image_bounds()
        self.crop_x = max(img_x, min(self.crop_x, img_x + img_w - self.crop_d))
        self.crop_y = max(img_y, min(self.crop_y, img_y + img_h - self.crop_d))

    def get_crop_bounds(self):
        return (self.crop_x, self.crop_y, self.crop_d, self.crop_d)


class ImageEditScreen(Screen):
    image_source = ObjectProperty(None)

    def on_enter(self, *args):
        view_image = self.manager.get_screen("view_image")
        if hasattr(view_image.ids, "image") and view_image.ids.image.source:
            # store the original path before any edits create temp files
            try:
                user_data['original_image_path'] = os.path.abspath(view_image.ids.image.source)
                # also store the original filename (basename) for downstream heuristics
                try:
                    user_data['original_filename'] = os.path.basename(user_data['original_image_path'])
                except Exception:
                    user_data['original_filename'] = view_image.ids.image.source
            except Exception:
                user_data['original_image_path'] = view_image.ids.image.source
                try:
                    user_data['original_filename'] = os.path.basename(user_data['original_image_path'])
                except Exception:
                    user_data['original_filename'] = view_image.ids.image.source

            self.ids.edit_image.source = view_image.ids.image.source
            self.ids.edit_image.reload()

        if not hasattr(self, "crop_overlay"):
            self.crop_overlay = SimpleCropOverlay()
            self.ids.edit_image.parent.add_widget(self.crop_overlay)

        self.crop_overlay.set_image_widget(self.ids.edit_image)
        Clock.schedule_once(lambda dt: self.crop_overlay.center_crop(), 0.1)

    def confirm(self):
        result_screen = self.manager.get_screen("result")
        if hasattr(result_screen.ids, "result_image"):
            result_screen.ids.result_image.source = self.ids.edit_image.source
            result_screen.ids.result_image.reload()
        self.manager.current = "result"

    def apply_filter(self, filter_name):
        current_image_path = self.ids.edit_image.source
        if not current_image_path or not os.path.exists(current_image_path):
            print("No image to apply filter to.")
            return
        try:
            img = PILImage.open(current_image_path)
            if filter_name == "grayscale":
                img = ImageOps.grayscale(img).convert("RGB")
            elif filter_name == "invert":
                img = ImageOps.invert(img.convert("RGB"))
            temp_path = self._save_to_temp(img, current_image_path)
            self.ids.edit_image.source = temp_path
            self.ids.edit_image.reload()
            Clock.schedule_once(lambda dt: self.crop_overlay.center_crop(), 0.1)
            print(f"Applied filter: {filter_name}")
        except Exception as e:
            print("Error applying filter:", e)

    def rotate_image(self):
        current_image_path = self.ids.edit_image.source
        if not current_image_path or not os.path.exists(current_image_path):
            print("No image to rotate.")
            return
        try:
            img = PILImage.open(current_image_path)
            img = img.rotate(-90, expand=True)
            temp_path = self._save_to_temp(img, current_image_path)
            self.ids.edit_image.source = temp_path
            self.ids.edit_image.reload()
            Clock.schedule_once(lambda dt: self.crop_overlay.center_crop(), 0.1)
            print("Rotated image by 90 degrees.")
        except Exception as e:
            print("Error rotating image:", e)

    def crop_image(self):
        current_image_path = self.ids.edit_image.source
        if not current_image_path or not os.path.exists(current_image_path):
            print("No image to crop.")
            return

        try:
            pil_img = PILImage.open(current_image_path)
            img_w, img_h = pil_img.size

            img_x, img_y, img_w_disp, img_h_disp = self.crop_overlay.get_image_bounds()
            crop_x, crop_y, crop_d, _ = self.crop_overlay.get_crop_bounds()

            rel_left = (crop_x - img_x) / img_w_disp
            rel_right = (crop_x + crop_d - img_x) / img_w_disp
            rel_bottom = (crop_y - img_y) / img_h_disp
            rel_top = (crop_y + crop_d - img_y) / img_h_disp

            rel_left = max(0, min(1, rel_left))
            rel_right = max(0, min(1, rel_right))
            rel_bottom = max(0, min(1, rel_bottom))
            rel_top = max(0, min(1, rel_top))

            pil_left = int(rel_left * img_w)
            pil_right = int(rel_right * img_w)
            pil_top = int((1 - rel_top) * img_h)
            pil_bottom = int((1 - rel_bottom) * img_h)

            left = min(pil_left, pil_right)
            right = max(pil_left, pil_right)
            upper = min(pil_top, pil_bottom)
            lower = max(pil_top, pil_bottom)

            if right <= left or lower <= upper:
                print("Invalid crop area.")
                return

            cropped = pil_img.crop((left, upper, right, lower))

            # Apply circular mask
            mask = PILImage.new("L", cropped.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, cropped.size[0], cropped.size[1]), fill=255)
            cropped.putalpha(mask)

            temp_path = self._save_to_temp(cropped, current_image_path)
            self.ids.edit_image.source = temp_path
            self.ids.edit_image.reload()
            print("Cropped image saved to:", temp_path)
            Clock.schedule_once(lambda dt: self.crop_overlay.center_crop(), 0.1)

        except Exception as e:
            print("Error cropping image:", e)

    def _save_to_temp(self, pil_img, orig_path):
        # Keep original extension when possible; otherwise default to .png
        ext = os.path.splitext(orig_path)[1].lower() if orig_path else ""
        if not ext:
            ext = ".png"
        # Attempt to include the original filename in the temp name for downstream heuristics
        orig_for_name = user_data.get('original_image_path') or orig_path or ""
        base_name = os.path.splitext(os.path.basename(orig_for_name))[0] if orig_for_name else ''
        # sanitize base_name to filesystem-safe token
        if base_name:
            safe_base = re.sub(r'[^A-Za-z0-9._-]', '_', base_name)
            name = f"{safe_base}_edit_{uuid.uuid4().hex}{ext}"
        else:
            name = f"edit_{uuid.uuid4().hex}{ext}"
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, name)

        # Map extension to PIL format
        fmt = None
        if ext in (".jpg", ".jpeg"):
            fmt = "JPEG"
        elif ext == ".png":
            fmt = "PNG"

        try:
            if fmt:
                pil_img.save(temp_path, fmt)
            else:
                pil_img.save(temp_path)
        except Exception:
            # fallback to PNG
            temp_path = os.path.join(temp_dir, f"edit_{uuid.uuid4().hex}.png")
            pil_img.save(temp_path, "PNG")

        return temp_path
