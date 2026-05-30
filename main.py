import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import threading
import customtkinter as ctk
from views.welcome_view import WelcomeView
from utils.webhook_server import start_server
from utils.scheduler import BookingScheduler

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # Set initial geometry to screen size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Delay zoomed state to ensure it applies after window creation
        self.after(0, lambda: self.state('zoomed'))
        self.bind("<Escape>", lambda e: self.destroy())
        self.show_welcome_view()

    def show_welcome_view(self):
        for widget in self.winfo_children():
            widget.destroy()
        welcome_view = WelcomeView(self)
        welcome_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    
    scheduler = BookingScheduler()
    scheduler.start()

    app = MainApp()
    app.mainloop()
