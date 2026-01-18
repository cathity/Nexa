import tkinter as tk
from tkinter import font as tkfont
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from auth_frames import StartPage, LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, EmailVerificationPage
    from notepad_frame import NotepadApplication
    from calendar_frame import CalendarApplication
    from friends_frame import FriendsPage

    print("Wszystko zostalo zaimportowane")
except ImportError as e:
    print(f"Blad importu: {e}")
    traceback.print_exc()
    input("Naciśnij Enter aby wyjść...")
    sys.exit(1)



class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Nexa")
        self.geometry("800x600")
        self.minsize(600, 400)


        self.themes = {
            "light": {
                "bg_primary": "#f0f0f0",
                "bg_secondary": "white",
                "bg_accent": "#2c3e50",  # Tło strony startowej
                "fg_primary": "black",
                "fg_accent": "#ecf0f1",  # Tekst na stronie startowej
                "entry_bg": "white",
                "entry_fg": "black",
                "list_bg": "#f0f0f0",
                "list_fg": "black",
                "list_highlight": "#3498db",  # Kolor zaznaczenia na liście
            },
            "dark": {
                "bg_primary": "#2c3e50",  # Ciemne tło główne
                "bg_secondary": "#34495e",  # Ciemne tło edytora
                "bg_accent": "#2c3e50",
                "fg_primary": "#ecf0f1",  # Jasny tekst
                "fg_accent": "#ecf0f1",
                "entry_bg": "#34495e",
                "entry_fg": "#ecf0f1",
                "list_bg": "#2c3e50",
                "list_fg": "#ecf0f1",
                "list_highlight": "#3498db",
            }
        }
        self.current_theme = "light"  # Motyw startowy
        self.colors = self.themes[self.current_theme]


        self.title_font = tkfont.Font(family='Helvetica', size=36, weight="bold")
        self.button_font = tkfont.Font(family='Helvetica', size=14)
        self.label_font = tkfont.Font(family='Helvetica', size=12)


        self.container = tk.Frame(self, bg=self.colors["bg_primary"])
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)


        frames_list = [StartPage, LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage,  EmailVerificationPage, NotepadApplication, CalendarApplication, FriendsPage]

        self.frames = {}
        for F in frames_list:
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        #motyw do wszystkich ramek przy starcie
        self.apply_theme()


        self.show_frame("StartPage")

    def show_frame(self, page_name, user_data=None):
        '''Podnosi wybraną ramkę na wierzch i zarządza menu'''
        frame = self.frames[page_name]

        if page_name == "NotepadApplication":
            if user_data:
                frame.set_current_user(user_data["id"])
            frame.create_notepad_menu()
        elif page_name == "CalendarApplication":
            if user_data:
                frame.set_current_user(user_data["id"])
            frame.create_calendar_menu()
        elif page_name == "FriendsPage":  # OBSŁUGA PRZYJACIÓŁ
            if user_data:
               frame.set_current_user(user_data["id"])
            empty_menu = tk.Menu(self)
            self.config(menu=empty_menu)
        else:
            empty_menu = tk.Menu(self)
            self.config(menu=empty_menu)

        frame.tkraise()
        self.apply_theme()

    def get_frame(self, page_name):
        return self.frames[page_name]

    def quit_app(self):
        self.destroy()


    def apply_theme(self):
        '''Stosuje bieżący motyw do wszystkich ramek'''
        self.colors = self.themes[self.current_theme]
        self.container.config(bg=self.colors["bg_primary"])
        try:
            self.config(menu=self.menubar)
        except AttributeError:
            pass  # Brak menu, nic nie rób

        for frame in self.frames.values():
            frame.update_theme(self.colors)

    def toggle_theme(self):
        '''Przełącza motyw między jasnym a ciemnym'''
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"

        self.apply_theme()



if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
