import json
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
import re
import webbrowser
import threading
import http.server
import socketserver
import os

class ColorReplacerApp:
    def __init__(self, root, json_data):
        self.root = root
        self.root.title("JSON Animation Color Replacer")

        self.json_data = json_data
        self.colors = []

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')

        self.render_frame = tk.Frame(self.notebook)
        self.colors_frame = tk.Frame(self.notebook)

        self.notebook.add(self.render_frame, text='Rendered JSON')
        self.notebook.add(self.colors_frame, text='Colors')

        self.canvas = tk.Canvas(self.render_frame, bg='white')
        self.canvas.pack(expand=1, fill='both')

        self.color_frame_container = tk.Frame(self.colors_frame)
        self.color_frame_container.pack(expand=1, fill='both')

        self.color_frame_canvas = tk.Canvas(self.color_frame_container)
        self.color_frame_canvas.pack(side=tk.LEFT, fill='both', expand=1)

        self.scrollbar = ttk.Scrollbar(self.color_frame_container, orient='vertical', command=self.color_frame_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        self.color_frame_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.color_frame_canvas.bind('<Configure>', lambda e: self.color_frame_canvas.configure(scrollregion=self.color_frame_canvas.bbox("all")))

        self.color_frame = tk.Frame(self.color_frame_canvas)
        self.color_frame_canvas.create_window((0, 0), window=self.color_frame, anchor='nw')

        self.save_button = tk.Button(self.colors_frame, text="Save Changes", command=self.save_json)
        self.save_button.pack(pady=10)

        self.display_json()
        self.extract_colors()
        self.display_colors()

    def display_json(self):
        self.canvas.delete('all')
        def draw_shapes(data):
            if isinstance(data, dict):
                if 'type' in data and 'color' in data:
                    if data['type'] == 'circle':
                        self.canvas.create_oval(50, 50, 150, 150, fill=data['color'])
                    elif data['type'] == 'square':
                        self.canvas.create_rectangle(200, 50, 300, 150, fill=data['color'])
                    elif data['type'] == 'triangle':
                        self.canvas.create_polygon(400, 150, 350, 50, 450, 50, fill=data['color'])
                for key, value in data.items():
                    draw_shapes(value)
            elif isinstance(data, list):
                for item in data:
                    draw_shapes(item)

        draw_shapes(self.json_data)

    def extract_colors(self):
        self.colors = []
        def find_colors(obj, path=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'k' and isinstance(value, list) and len(value) == 4:
                        if all(isinstance(i, (int, float)) for i in value):
                            color = "#{:02x}{:02x}{:02x}".format(int(value[0] * 255), int(value[1] * 255), int(value[2] * 255))
                            self.colors.append((path + '.' + key if path else key, color))
                    else:
                        find_colors(value, path + '.' + key if path else key)
            elif isinstance(obj, list):
                for index, item in enumerate(obj):
                    find_colors(item, f"{path}[{index}]")

        find_colors(self.json_data)
        print("Colors found:", self.colors)  # Debug output

    def display_colors(self):
        for widget in self.color_frame.winfo_children():
            widget.destroy()

        for path, color in self.colors:
            frame = tk.Frame(self.color_frame)
            frame.pack(fill=tk.X, padx=2, pady=2)
            color_label = tk.Label(frame, text=color, bg=color, width=10)
            color_label.pack(side=tk.LEFT, padx=5)
            path_label = tk.Label(frame, text=path, anchor="w")
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            replace_button = tk.Button(frame, text="Replace", command=lambda p=path, c=color: self.on_replace_click(p, c))
            replace_button.pack(side=tk.RIGHT, padx=5)

        self.save_button = tk.Button(self.colors_frame, text="Save Changes", command=self.save_json)
        self.save_button.pack(pady=10)

    def is_color(self, string):
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', string))

    def on_replace_click(self, path, color):
        new_color = colorchooser.askcolor(title="Choose new color", initialcolor=color)[1]
        if new_color:
            self.replace_color_in_json(self.json_data, path, new_color)
            self.extract_colors()
            self.display_colors()
            self.display_json()

    def replace_color_in_json(self, obj, path, new_color):
        keys = path.replace('[', '.[').split('.')
        for key in keys[:-1]:
            if key.isdigit():
                obj = obj[int(key)]
            elif key.startswith('['):
                obj = obj[int(key[1:-1])]
            else:
                obj = obj[key]
        last_key = keys[-1]
        new_color_value = [int(new_color[i:i+2], 16) / 255 for i in (1, 3, 5)] + [1]
        if last_key.isdigit():
            obj[int(last_key)] = new_color_value
        elif last_key.startswith('['):
            obj[int(last_key[1:-1])] = new_color_value
        else:
            obj[last_key] = new_color_value

    def save_json(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.json_data, file, indent=4)
            messagebox.showinfo("Save Successful", "The JSON file has been saved successfully.")

def load_json():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                with open('animation.json', 'w') as animation_file:
                    json.dump(data, animation_file)
                messagebox.showinfo("Success", "JSON file loaded successfully.")
                global json_data, json_file_path
                json_data = data
                json_file_path = file_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")

def preview_json():
    if json_data:
        preview_path = "index.html"
        if os.path.exists(preview_path):
            # Start a simple HTTP server to serve index.html and animation.json
            def serve():
                os.chdir(os.path.dirname(preview_path))
                handler = http.server.SimpleHTTPRequestHandler
                with socketserver.TCPServer(("", 8000), handler) as httpd:
                    print("Serving at port 8000")  # Debug output
                    httpd.serve_forever()

            threading.Thread(target=serve, daemon=True).start()
            webbrowser.open("http://localhost:8000/index.html")
        else:
            messagebox.showerror("Error", "index.html not found.")
    else:
        messagebox.showerror("Error", "No JSON file loaded.")

def replace_colors():
    if json_data:
        new_window = tk.Toplevel(root)
        app = ColorReplacerApp(new_window, json_data)
        new_window.geometry("800x600")
    else:
        messagebox.showerror("Error", "No JSON file loaded.")

# Initialize global variables
json_data = None
json_file_path = None

# Create main window
root = tk.Tk()
root.title("JSON File Editor")

# Set the window icon
root.iconbitmap("your_logo.ico")  # Replace 'your_logo.ico' with the path to your icon file

# Create buttons
load_button = tk.Button(root, text="Load JSON File", command=load_json)
preview_button = tk.Button(root, text="Preview JSON File", command=preview_json)
replace_colors_button = tk.Button(root, text="Replace Colors", command=replace_colors)

# Place buttons
load_button.pack(pady=10)
preview_button.pack(pady=10)
replace_colors_button.pack(pady=10)

# Run the application
root.mainloop()
