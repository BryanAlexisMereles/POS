import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")
        
        try:
            self.df = pd.read_csv("usuarios.csv")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo Excel: {e}")
            return

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.login_frame, text="Iniciar Sesión", command=self.validate_login).grid(row=2, column=0, columnspan=2, pady=10)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.df['usuario'].values:
            user_data = self.df[self.df['usuario'] == username].iloc[0]
            if user_data['clave'] == password:
                self.root.destroy()  # Cerrar ventana de login
                os.system("python main_app.py")  # Ejecutar el segundo script
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
        else:
            messagebox.showerror("Error", "Usuario no encontrado")

def generarLogin():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    generarLogin()