import http.server
import socketserver
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser

PORT = 8000

def choose_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if not file_path:
        messagebox.showerror("File Error", "No file was selected.")
        return None
    return file_path

def start_server(json_file_path):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/animation.json':
                self.path = 'animation.json'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        httpd.serve_forever()

if __name__ == "__main__":
    json_file = choose_file()
    if json_file:
        shutil.copyfile(json_file, 'animation.json')  # Copy the JSON file to the current directory
        start_server('animation.json')
