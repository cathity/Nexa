
import tkinter as tk
from tkinter import font as tkfont, messagebox

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label_title = tk.Label(self.center_frame, text="Nexa", font=controller.title_font)
        self.label_title.pack(pady=(0, 40))

        btn_login = tk.Button(self.center_frame, text="Zaloguj się",
                              font=controller.button_font,
                              bg="#3498db", fg="#ecf0f1", relief="flat",
                              padx=20, pady=10,
                              command=lambda: controller.show_frame("LoginPage"))
        btn_login.pack(pady=10, fill="x")

        btn_register = tk.Button(self.center_frame, text="Zarejestruj się",
                                 font=controller.button_font,
                                 bg="#2ecc71", fg="#ecf0f1", relief="flat",
                                 padx=20, pady=10,
                                 command=lambda: controller.show_frame("RegisterPage"))
        btn_register.pack(pady=10, fill="x")

        btn_quit = tk.Button(self.center_frame, text="Wyjdź z aplikacji",
                             font=controller.button_font,
                             bg="#e74c3c", fg="#ecf0f1", relief="flat",
                             padx=20, pady=10,
                             command=controller.quit_app)
        btn_quit.pack(pady=(30, 0), fill="x")

    def update_theme(self, colors):
        '''Aktualizuje kolory dla motywu'''
        self.config(bg=colors["bg_accent"])
        self.center_frame.config(bg=colors["bg_accent"])
        self.label_title.config(bg=colors["bg_accent"], fg=colors["fg_accent"])



class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Ekran Logowania", font=controller.title_font)
        self.label.pack(pady=40)

        self.login_label = tk.Label(self, text="Login:", font=controller.label_font)
        self.login_label.pack(pady=(10, 0))
        self.login_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.login_entry.pack(pady=5, ipady=4)

        self.pass_label = tk.Label(self, text="Hasło:", font=controller.label_font)
        self.pass_label.pack(pady=(10, 0))
        self.pass_entry = tk.Entry(self, show="*", font=controller.label_font, width=30, relief="solid", bd=1)
        self.pass_entry.pack(pady=5, ipady=4)

        from auth_controller import login_user

        def try_login():
            username = self.login_entry.get()
            password = self.pass_entry.get()

            user_data = login_user(username, password)
            if user_data:
                if not user_data.get("verified", True):
                    messagebox.showwarning("Email niezweryfikowany",
                                           "Twój email nie został jeszcze zweryfikowany.\n"
                                           "Sprawdź skrzynkę pocztową i wprowadź kod weryfikacyjny.")
                else:
                    controller.show_frame("NotepadApplication", user_data)
            else:
                messagebox.showerror("Błąd", "Niepoprawny login lub hasło.")


        self.login_btn = tk.Button(
            self, text="Zaloguj",
            font=controller.button_font,
            bg="#3498db", fg="white",
            command=try_login
        )
        self.login_btn.pack(pady=20, ipadx=10, ipady=5)


        self.forgot_btn = tk.Button(
            self, text="Zapomniałem hasła",
            font=controller.button_font,
            bg="#f39c12", fg="white",
            command=lambda: controller.show_frame("ForgotPasswordPage")
        )
        self.forgot_btn.pack(pady=10, ipadx=10, ipady=5)

        self.back_btn = tk.Button(self, text="Wróć",
                                  font=controller.button_font,
                                  bg="#95a5a6", fg="white",
                                  command=lambda: controller.show_frame("StartPage"))
        self.back_btn.pack(pady=10, ipadx=10, ipady=5)

    def update_theme(self, colors):
        '''Aktualizuje kolory dla motywu'''
        self.config(bg=colors["bg_primary"])
        self.label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.login_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.pass_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])

        self.login_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.pass_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])



class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Ekran Rejestracji", font=controller.title_font)
        self.label.pack(pady=40)

        self.login_label = tk.Label(self, text="Login:", font=controller.label_font)
        self.login_label.pack(pady=(10, 0))
        self.reg_login_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.reg_login_entry.pack(pady=5, ipady=4)

        self.email_label = tk.Label(self, text="Email:", font=controller.label_font)
        self.email_label.pack(pady=(10, 0))
        self.reg_email_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.reg_email_entry.pack(pady=5, ipady=4)

        self.pass1_label = tk.Label(self, text="Hasło:", font=controller.label_font)
        self.pass1_label.pack(pady=(10, 0))
        self.reg_pass1_entry = tk.Entry(self, show="*", font=controller.label_font, width=30, relief="solid", bd=1)
        self.reg_pass1_entry.pack(pady=5, ipady=4)

        self.pass2_label = tk.Label(self, text="Powtórz hasło:", font=controller.label_font)
        self.pass2_label.pack(pady=(10, 0))
        self.reg_pass2_entry = tk.Entry(self, show="*", font=controller.label_font, width=30, relief="solid", bd=1)
        self.reg_pass2_entry.pack(pady=5, ipady=4)

        from auth_controller import validate_registration, register_user

        def try_register():
            username = self.reg_login_entry.get()
            email = self.reg_email_entry.get()
            p1 = self.reg_pass1_entry.get()
            p2 = self.reg_pass2_entry.get()

            ok, msg = validate_registration(username, email, p1, p2)
            if not ok:
                messagebox.showerror("Błąd", msg)
                return

            ok, msg = register_user(username, email, p1)
            if ok:
                messagebox.showinfo("Sukces", "Konto zostało utworzone!")
                verification_page = controller.get_frame("EmailVerificationPage")
                verification_page.set_email(email)
                controller.show_frame("EmailVerificationPage")
            else:
                messagebox.showerror("Błąd", msg)

        self.register_btn = tk.Button(
            self, text="Zarejestruj",
            font=controller.button_font,
            bg="#2ecc71", fg="white",
            command=try_register
        )
        self.register_btn.pack(pady=20, ipadx=10, ipady=5)

        self.back_btn = tk.Button(self, text="Wróć",
                                  font=controller.button_font,
                                  bg="#95a5a6", fg="white",
                                  command=lambda: controller.show_frame("StartPage"))
        self.back_btn.pack(pady=10, ipadx=10, ipady=5)

    def update_theme(self, colors):
        '''Aktualizuje kolory dla motywu'''
        self.config(bg=colors["bg_primary"])
        self.label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.login_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.email_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.pass1_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.pass2_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])

        self.reg_login_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.reg_email_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.reg_pass1_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.reg_pass2_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])


class ForgotPasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.label = tk.Label(self, text="Resetowanie Hasła", font=controller.title_font)
        self.label.pack(pady=40)

        self.email_label = tk.Label(self, text="Email:", font=controller.label_font)
        self.email_label.pack(pady=(10, 0))
        self.email_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.email_entry.pack(pady=5, ipady=4)

        from auth_controller import set_reset_code

        def request_code():
            email = self.email_entry.get()
            if not email or "@" not in email:
                messagebox.showerror("Błąd", "Podaj poprawny adres email.")
                return

            # loading message
            self.request_btn.config(state="disabled", text="Wysyłanie...")
            self.update()

            success, result = set_reset_code(email)

            self.request_btn.config(state="normal", text="Wyślij kod resetujący")

            if success:
                messagebox.showinfo("Kod wysłany",
                                    "Kod resetujący został wysłany na podany adres email.\n\n"
                                    "Sprawdź swoją skrzynkę pocztową (oraz folder SPAM).")
                controller.show_frame("ResetPasswordPage")
                reset_page = controller.get_frame("ResetPasswordPage")
                reset_page.set_email(email)
            else:
                messagebox.showerror("Błąd", result)

        self.request_btn = tk.Button(
            self, text="Wyślij kod resetujący",
            font=controller.button_font,
            bg="#3498db", fg="white",
            command=request_code
        )
        self.request_btn.pack(pady=20, ipadx=10, ipady=5)

        self.back_btn = tk.Button(self, text="Wróć",
                                  font=controller.button_font,
                                  bg="#95a5a6", fg="white",
                                  command=lambda: controller.show_frame("LoginPage"))
        self.back_btn.pack(pady=10, ipadx=10, ipady=5)

    def update_theme(self, colors):
        '''Aktualizuje kolory dla motywu'''
        self.config(bg=colors["bg_primary"])
        self.label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.email_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.email_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])


class ResetPasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.email = ""

        self.label = tk.Label(self, text="Ustaw Nowe Hasło", font=controller.title_font)
        self.label.pack(pady=40)

        self.code_label = tk.Label(self, text="Kod resetujący:", font=controller.label_font)
        self.code_label.pack(pady=(10, 0))
        self.code_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.code_entry.pack(pady=5, ipady=4)

        self.pass1_label = tk.Label(self, text="Nowe hasło:", font=controller.label_font)
        self.pass1_label.pack(pady=(10, 0))
        self.pass1_entry = tk.Entry(self, show="*", font=controller.label_font, width=30, relief="solid", bd=1)
        self.pass1_entry.pack(pady=5, ipady=4)

        self.pass2_label = tk.Label(self, text="Powtórz hasło:", font=controller.label_font)
        self.pass2_label.pack(pady=(10, 0))
        self.pass2_entry = tk.Entry(self, show="*", font=controller.label_font, width=30, relief="solid", bd=1)
        self.pass2_entry.pack(pady=5, ipady=4)

        from auth_controller import reset_password

        def perform_reset():
            code = self.code_entry.get()
            new_password = self.pass1_entry.get()
            confirm_password = self.pass2_entry.get()

            if not code or len(code) != 6:
                messagebox.showerror("Błąd", "Podaj 6-cyfrowy kod resetujący.")
                return

            if new_password != confirm_password:
                messagebox.showerror("Błąd", "Hasła nie są identyczne.")
                return

            if len(new_password) < 6:
                messagebox.showerror("Błąd", "Hasło musi mieć co najmniej 6 znaków.")
                return

            success, message = reset_password(self.email, code, new_password)
            if success:
                messagebox.showinfo("Sukces", message)
                controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Błąd", message)

        self.reset_btn = tk.Button(
            self, text="Zresetuj hasło",
            font=controller.button_font,
            bg="#2ecc71", fg="white",
            command=perform_reset
        )
        self.reset_btn.pack(pady=20, ipadx=10, ipady=5)

        self.back_btn = tk.Button(self, text="Wróć",
                                  font=controller.button_font,
                                  bg="#95a5a6", fg="white",
                                  command=lambda: controller.show_frame("ForgotPasswordPage"))
        self.back_btn.pack(pady=10, ipadx=10, ipady=5)

    def set_email(self, email):
        self.email = email

    def update_theme(self, colors):
        '''Aktualizuje kolory dla motywu'''
        self.config(bg=colors["bg_primary"])
        self.label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.code_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.pass1_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.pass2_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])

        self.code_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.pass1_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])
        self.pass2_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])


class EmailVerificationPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.email = ""

        self.label = tk.Label(self, text="Weryfikacja Emaila", font=controller.title_font)
        self.label.pack(pady=40)

        self.info_label = tk.Label(self, text="Wprowadź 6-cyfrowy kod wysłany na Twój email:",
                                  font=controller.label_font, wraplength=400)
        self.info_label.pack(pady=(10, 20))

        self.code_label = tk.Label(self, text="Kod weryfikacyjny:", font=controller.label_font)
        self.code_label.pack(pady=(10, 0))
        self.code_entry = tk.Entry(self, font=controller.label_font, width=30, relief="solid", bd=1)
        self.code_entry.pack(pady=5, ipady=4)

        from auth_controller import verify_email_code, resend_verification_code

        def verify_code():
            code = self.code_entry.get()
            if not code or len(code) != 6:
                messagebox.showerror("Błąd", "Podaj 6-cyfrowy kod weryfikacyjny.")
                return

            success, message = verify_email_code(self.email, code)
            if success:
                messagebox.showinfo("Sukces", message)
                controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Błąd", message)

        def resend_code():
            success, message = resend_verification_code(self.email)
            if success:
                messagebox.showinfo("Kod wysłany", message)
            else:
                messagebox.showerror("Błąd", message)

        self.verify_btn = tk.Button(
            self, text="Zweryfikuj email",
            font=controller.button_font,
            bg="#27ae60", fg="white",
            command=verify_code
        )
        self.verify_btn.pack(pady=20, ipadx=10, ipady=5)

        self.resend_btn = tk.Button(
            self, text="Wyślij nowy kod",
            font=controller.button_font,
            bg="#3498db", fg="white",
            command=resend_code
        )
        self.resend_btn.pack(pady=10, ipadx=10, ipady=5)

        self.back_btn = tk.Button(self, text="Wróć do logowania",
                                  font=controller.button_font,
                                  bg="#95a5a6", fg="white",
                                  command=lambda: controller.show_frame("LoginPage"))
        self.back_btn.pack(pady=10, ipadx=10, ipady=5)

    def set_email(self, email):
        self.email = email
        self.info_label.config(text=f"Wprowadź 6-cyfrowy kod wysłany na:\n{email}")

    def update_theme(self, colors):
        self.config(bg=colors["bg_primary"])
        self.label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.info_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.code_label.config(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self.code_entry.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_primary"])

