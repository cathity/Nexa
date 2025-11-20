import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "nexayour.app@gmail.com"
EMAIL_PASSWORD = "cvku kasw ooyw vxzf"


def send_reset_code(to_email, code):
    msg = MIMEMultipart()
    msg['Subject'] = "Kod resetowania hasła - Nexa"
    msg['From'] = f"Nexa App <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
          .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
          .header {{ background: #3498db; color: white; padding: 20px; text-align: center; }}
          .content {{ background: #f9f9f9; padding: 20px; }}
          .code {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; }}
          .footer {{ background: #ecf0f1; padding: 15px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Nexa</h1>
            <p>Resetowanie hasła</p>
          </div>
          <div class="content">
            <h2>Witaj!</h2>
            <p>Otrzymaliśmy prośbę o resetowanie hasła dla Twojego konta w aplikacji Nexa.</p>
            <p>Użyj poniższego kodu w aplikacji, aby ustawić nowe hasło:</p>
            <div class="code">{code}</div>
            <p><strong>Kod jest ważny przez 1 godzinę.</strong></p>
            <p>Jeśli to nie Ty wysłałeś tę prośbę, zignoruj tę wiadomość - Twoje konto pozostanie bezpieczne.</p>
          </div>
          <div class="footer">
            <p>© 2024 Nexa App. Wszelkie prawa zastrzeżone.</p>
            <p>Wiadomość wygenerowana automatycznie, prosimy na nią nie odpowiadać.</p>
          </div>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        # Dodaj timeout dla bezpieczeństwa
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"Email z kodem resetującym wysłany do: {to_email}")
            return True
    except smtplib.SMTPAuthenticationError:
        print("Błąd uwierzytelniania - sprawdź login i hasło")
        return False
    except smtplib.SMTPException as e:
        print(f"Błąd SMTP: {e}")
        return False
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return False

# 👇 DODAJ NOWĄ FUNKCJĘ - PO ISTNIEJĄCEJ
def send_verification_email(to_email, code):
    """Wysyła email weryfikacyjny przy rejestracji"""
    msg = MIMEMultipart()
    msg['Subject'] = "Weryfikacja adresu email - Nexa"
    msg['From'] = f"Nexa App <{EMAIL_ADDRESS}>"
    msg['To'] = to_email

    html_content = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
          .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
          .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
          .content {{ background: #f9f9f9; padding: 20px; }}
          .code {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; }}
          .footer {{ background: #ecf0f1; padding: 15px; text-align: center; font-size: 12px; color: #7f8c8d; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>Nexa</h1>
            <p>Weryfikacja adresu email</p>
          </div>
          <div class="content">
            <h2>Witaj w Nexa!</h2>
            <p>Dziękujemy za rejestrację. Aby aktywować swoje konto, użyj poniższego kodu weryfikacyjnego:</p>
            <div class="code">{code}</div>
            <p><strong>Kod jest ważny przez 24 godziny.</strong></p>
            <p>Wprowadź ten kod w aplikacji Nexa, aby zakończyć proces rejestracji.</p>
            <p>Jeśli to nie Ty zakładałeś konto, zignoruj tę wiadomość.</p>
          </div>
          <div class="footer">
            <p>© 2024 Nexa App. Wszelkie prawa zastrzeżone.</p>
            <p>Wiadomość wygenerowana automatycznie, prosimy na nią nie odpowiadać.</p>
          </div>
        </div>
      </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"Email weryfikacyjny wysłany do: {to_email}")
            return True
    except Exception as e:
        print(f"Błąd wysyłania emaila weryfikacyjnego: {e}")
        return False