import os
import random
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

class ImageGallery(Tk):
    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")
        else:
            self.canvas.yview_scroll(int(event.num == 5) - int(event.num == 4), "units")

    def close_viewer(self):
        self.viewer.withdraw()

    def __init__(self):
        super().__init__()
        self.title("Pinsplorer")
        self.geometry("1200x800")

        self.folder = None
        self.images = []
        self.thumbs = {}  # Cache: {path -> PhotoImage}
        self.thumb_size = 150
        self.current_index = None

        self._build_ui()

    def _build_ui(self):
        top = Frame(self)
        top.pack(fill=X)

        Button(top, text="Select Folder", command=self.select_folder).pack(side=LEFT)
        Button(top, text="Randomize", command=self.randomize).pack(side=LEFT)
        Button(top, text="Sort A-Z", command=lambda: self.sort_images(True)).pack(side=LEFT)
        Button(top, text="Sort Z-A", command=lambda: self.sort_images(False)).pack(side=LEFT)

        Scale(
            top, from_=64, to=300, orient=HORIZONTAL,
            label="Thumbnail Size", command=self.resize_thumbs
        ).pack(side=LEFT)

        self.canvas = Canvas(self)
        self.scroll = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)

        self.scroll.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

        self.viewer = Toplevel(self)
        self.viewer.withdraw()
        self.viewer.configure(bg="black")
        self.viewer.bind("<Escape>", lambda e: self.close_viewer())
        self.viewer.bind("<Button-1>", self.on_viewer_click)
        self.viewer.bind("<Left>", lambda e: self.show_prev())
        self.viewer.bind("<Right>", lambda e: self.show_next())

        self.viewer_label = Label(self.viewer, bg="black")
        self.viewer_label.pack(fill=BOTH, expand=True)

        self.viewer_label.bind("<Button-1>", lambda e: None)

        nav = Frame(self.viewer, bg="black")
        nav.pack(fill=X)
        Button(nav, text="◀", command=self.show_prev).pack(side=LEFT)
        Button(nav, text="▶", command=self.show_next).pack(side=RIGHT)

    def select_folder(self):
        self.folder = filedialog.askdirectory()
        if not self.folder:
            return
        self.images = [
            os.path.join(self.folder, f)
            for f in os.listdir(self.folder)
            if f.lower().endswith(IMAGE_EXTS)
        ]
        self.images.sort()
        self.preload_thumbnails()
        self.render_thumbnails()

    def preload_thumbnails(self):
        self.thumbs.clear()
        for path in self.images:
            try:
                img = Image.open(path)
                img.thumbnail((self.thumb_size, self.thumb_size))
                self.thumbs[path] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load thumbnail for {path}: {e}")

    def render_thumbnails(self):
        for w in self.frame.winfo_children():
            w.destroy()

        cols = max(1, self.winfo_width() // (self.thumb_size + 20))

        for i, path in enumerate(self.images):
            tk_img = self.thumbs.get(path)
            if not tk_img:
                # fallback in case thumbnail missing
                try:
                    img = Image.open(path)
                    img.thumbnail((self.thumb_size, self.thumb_size))
                    tk_img = ImageTk.PhotoImage(img)
                    self.thumbs[path] = tk_img
                except Exception as e:
                    print(f"Failed to load image {path}: {e}")
                    continue

            btn = Button(self.frame, image=tk_img, command=lambda i=i: self.open_viewer(i))
            btn.grid(row=i // cols, column=i % cols, padx=5, pady=5)

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_thumbs(self, value):
        self.thumb_size = int(value)
        if hasattr(self, "_resize_after"):
            self.after_cancel(self._resize_after)
        self._resize_after = self.after(150, self._resize_and_render)

    def _resize_and_render(self):
        self.preload_thumbnails()
        self.render_thumbnails()

    def randomize(self):
        random.shuffle(self.images)
        self.render_thumbnails()

    def sort_images(self, asc):
        self.images.sort(reverse=not asc)
        self.render_thumbnails()

    def open_viewer(self, index):
        self.current_index = index
        self.viewer.deiconify()
        # Set viewer size and position
        self.viewer.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_x()}+{self.winfo_y()}")
        self.viewer.update_idletasks()  # Force geometry update here
        self.show_image()

    def show_image(self):
        path = self.images[self.current_index]
        with Image.open(path) as img:
            vw, vh = self.viewer.winfo_width(), self.viewer.winfo_height()
            img.thumbnail((vw, vh))
            img_copy = img.copy()  # Copy to release the file handle
        self.viewer_img = ImageTk.PhotoImage(img_copy)
        self.viewer_label.config(image=self.viewer_img)

    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def show_next(self):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()

    def on_viewer_click(self, event):
        if event.widget == self.viewer:
            self.close_viewer()

if __name__ == "__main__":
    ImageGallery().mainloop()
