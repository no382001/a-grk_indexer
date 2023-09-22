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
        self.image_on_canvas = None
        self.rect_coords = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-3>", self.on_button_press_green)
        self.canvas.bind("<B3-Motion>", self.on_mouse_drag_green)
        self.canvas.bind("<ButtonRelease-3>", self.on_button_release_green)

        self.rect_green = None
        self.rect_coords_green = None
        self.start_x_green = None
        self.start_y_green = None

        self.pdf_path = filedialog.askopenfilename(title="Open PDF", filetypes=[("PDF Files", "*.pdf")])
        self.pages = convert_from_path(self.pdf_path)

        self.display_page(self.pages[0])

        btn_tokenize = tk.Button(root, text="Tokenize", command=self.tokenize)
        btn_tokenize.pack()

        self.root.bind("<Configure>", self.on_resize)

        self.prev_button = tk.Button(self.root, text="<< Prev", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        self.next_button = tk.Button(self.root, text="Next >>", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=10)

        self.current_page_num = 0

        self.display_page(self.pages[self.current_page_num])

    def display_page(self, page, resize_for_display=True):
        # Delete the previous image (if it exists) from the canvas
        if self.image_on_canvas:
            self.canvas.delete(self.image_on_canvas)

        # Display the new image
        if resize_for_display:
            width, height = self.root.winfo_width(), self.root.winfo_height()
            page = page.resize((width, height))
        self.current_image = ImageTk.PhotoImage(page)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)

        self.canvas.lower(self.image_on_canvas)

        # Ensure the rectangle is drawn or updated
        if not self.rect and self.rect_coords:
            self.rect = self.canvas.create_rectangle(*self.rect_coords, outline="red")
        elif self.rect:
            self.canvas.coords(self.rect, *self.rect_coords)

        # Ensure the green rectangle is drawn or updated
        if not self.rect_green and self.rect_coords_green:
            self.rect_green = self.canvas.create_rectangle(*self.rect_coords_green, outline="green")
        elif self.rect_green:
            self.canvas.coords(self.rect_green, *self.rect_coords_green)



    def prev_page(self):
        if self.current_page_num > 0:
            self.current_page_num -= 1
            self.display_page(self.pages[self.current_page_num])

    def next_page(self):
        if self.current_page_num < len(self.pages) - 1:
            self.current_page_num += 1
            self.display_page(self.pages[self.current_page_num])

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_button_release(self, event):
        self.rect_coords = self.canvas.coords(self.rect)
        pass

    def on_button_press_green(self, event):
        self.start_x_green = self.canvas.canvasx(event.x)
        self.start_y_green = self.canvas.canvasy(event.y)
        if self.rect_green:
            self.canvas.delete(self.rect_green)
        self.rect_green = self.canvas.create_rectangle(self.start_x_green, self.start_y_green, self.start_x_green, self.start_y_green, outline="green")

    def on_mouse_drag_green(self, event):
        self.canvas.coords(self.rect_green, self.start_x_green, self.start_y_green, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_button_release_green(self, event):
        self.rect_coords_green = self.canvas.coords(self.rect_green)


    def tokenize(self):
        results = []

        # Function to get OCR results given rectangle coordinates
        def get_ocr_for_coords(rect_coords, color):
            if rect_coords:
                scale_x = self.pages[0].width / self.root.winfo_width()
                scale_y = self.pages[0].height / self.root.winfo_height()

                # adjust the coordinates to match the original image size
                adjusted_coords = [rect_coords[0] * scale_x, rect_coords[1] * scale_y, rect_coords[2] * scale_x, rect_coords[3] * scale_y]

                for idx, page in enumerate(self.pages):
                    cropped = page.crop(adjusted_coords)
                    text = pytesseract.image_to_string(cropped, lang='grc')
                    tokens = text.split()  # basic tokenization
                    results.append((idx, tokens, color))

        get_ocr_for_coords(self.rect_coords, "red")
        get_ocr_for_coords(self.rect_coords_green, "green")

        for idx, tokens, color in results:
            print(f"Page {idx + 1} ({color} area): {tokens}")



    def on_resize(self, event):
        if hasattr(self, 'current_image'):
            self.display_page(self.pages[0])


root = tk.Tk()
app = App(root)
root.mainloop()
