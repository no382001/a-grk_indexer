import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageTk


class App:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
        self.init_attributes()

    def setup_gui(self):
        self.root.title("PDF Cropping and Tokenization")
        
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.prev_button = tk.Button(self.root, text="<< Prev", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(self.root, text="Next >>", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        btn_tokenize = tk.Button(self.root, text="Tokenize", command=self.tokenize)
        btn_tokenize.pack()
        
        self.root.bind("<Configure>", self.on_resize)

    def init_attributes(self):
        self.image_on_canvas = None
        self.rects = {
            "red": {"object": None, "coords": None, "start": None},
            "green": {"object": None, "coords": None, "start": None}
        }
        
        self.pdf_path = filedialog.askopenfilename(title="Open PDF", filetypes=[("PDF Files", "*.pdf")])
        self.pages = convert_from_path(self.pdf_path)
        self.current_page_num = 0

        self.display_page(self.pages[self.current_page_num])

        self.setup_bindings()

    def setup_bindings(self):
        bindings = {
            "<ButtonPress-1>": self.start_rectangle,
            "<B1-Motion>": self.drag_rectangle,
            "<ButtonRelease-1>": self.release_rectangle,
            "<ButtonPress-3>": self.start_green_rectangle,
            "<B3-Motion>": self.drag_green_rectangle,
            "<ButtonRelease-3>": self.release_green_rectangle
        }
        for event, handler in bindings.items():
            self.canvas.bind(event, handler)

    def start_rectangle(self, event):
        self.start_draw(event, "red")

    def drag_rectangle(self, event):
        self.drag_draw(event, "red")

    def release_rectangle(self, event):
        self.release_draw(event, "red")

    def start_green_rectangle(self, event):
        self.start_draw(event, "green")

    def drag_green_rectangle(self, event):
        self.drag_draw(event, "green")

    def release_green_rectangle(self, event):
        self.release_draw(event, "green")

    def start_draw(self, event, color):
        start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.rects[color]["start"] = start
        rect = self.canvas.create_rectangle(*start, *start, outline=color)
        self.rects[color]["object"] = rect

    def drag_draw(self, event, color):
        start_x, start_y = self.rects[color]["start"]
        self.canvas.coords(self.rects[color]["object"], start_x, start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def release_draw(self, event, color):
        self.rects[color]["coords"] = self.canvas.coords(self.rects[color]["object"])

    def display_page(self, page, resize_for_display=True):
        if self.image_on_canvas:
            self.canvas.delete(self.image_on_canvas)

        if resize_for_display:
            width, height = self.root.winfo_width(), self.root.winfo_height()
            page = page.resize((width, height))

        self.current_image = ImageTk.PhotoImage(page)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)

        self.update_rectangles()

    def update_rectangles(self):
        for color, data in self.rects.items():
            if data["object"]:
                self.canvas.delete(data["object"])
            if data["coords"]:
                data["object"] = self.canvas.create_rectangle(*data["coords"], outline=color)

    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.display_page(self.pages[self.current_page_num])

    def next_page(self):
        if self.current_page_num < len(self.pages) - 1:
            self.current_page_num += 1
            self.display_page(self.pages[self.current_page_num])

    def tokenize(self):
        results = []
        for color, data in self.rects.items():
            if data["coords"]:
                scale_x = self.pages[0].width / self.root.winfo_width()
                scale_y = self.pages[0].height / self.root.winfo_height()
                adjusted_coords = [data["coords"][0] * scale_x, data["coords"][1] * scale_y, data["coords"][2] * scale_x, data["coords"][3] * scale_y]
                for idx, page in enumerate(self.pages):
                    cropped = page.crop(adjusted_coords)
                    text = pytesseract.image_to_string(cropped, lang='grc')
                    tokens = text.split()  # basic tokenization
                    results.append((idx, tokens, color))

        for idx, tokens, color in results:
            print(f"Page {idx + 1} ({color} area): {tokens}")

    def on_resize(self, event):
        if hasattr(self, 'current_image'):
            self.display_page(self.pages[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
