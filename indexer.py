import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Cropping and Tokenization")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.pdf_path = filedialog.askopenfilename(title="Open PDF", filetypes=[("PDF Files", "*.pdf")])
        self.pages = convert_from_path(self.pdf_path)

        self.display_page(self.pages[0])

        btn_tokenize = tk.Button(root, text="Tokenize", command=self.tokenize)
        btn_tokenize.pack()

        self.root.bind("<Configure>", self.on_resize)

    def display_page(self, page, resize_for_display=True):
        if resize_for_display:
            width, height = self.root.winfo_width(), self.root.winfo_height()
            page = page.resize((width, height))
        self.current_image = ImageTk.PhotoImage(page)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_button_release(self, event):
        pass

    def tokenize(self):
        results = []

        if self.rect:
            rect_coords = self.canvas.coords(self.rect)

            # calculate the scaling factor
            scale_x = self.pages[0].width / self.root.winfo_width()
            scale_y = self.pages[0].height / self.root.winfo_height()

            # adjust the coordinates to match the original image size
            rect_coords = [rect_coords[0] * scale_x, rect_coords[1] * scale_y, rect_coords[2] * scale_x, rect_coords[3] * scale_y]

            for idx, page in enumerate(self.pages):
                cropped = page.crop(rect_coords)
                text = pytesseract.image_to_string(cropped, lang='grc')
                tokens = text.split()  # basic tokenization
                results.append((idx, tokens))

        for idx, tokens in results:
            print(f"Page {idx + 1}: {tokens}")


    def on_resize(self, event):
        if hasattr(self, 'current_image'):
            self.display_page(self.pages[0])


root = tk.Tk()
app = App(root)
root.mainloop()
