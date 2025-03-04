import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import datetime

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicación")
        self.root.geometry("1200x600")  # Aumenté el ancho para acomodar la barra lateral

        # Crear la barra lateral
        self.sidebar = tk.Frame(self.root, width=200, bg="#333333")  # Barra lateral gris oscuro
        self.sidebar.pack(side="left", fill="y")

        # Botones en la barra lateral
        tk.Button(self.sidebar, text="Gestión de Stock", bg="#333333", fg="white", command=self.show_stock).pack(fill="x", pady=10)
        tk.Button(self.sidebar, text="Ventas", bg="#333333", fg="white", command=self.show_sales).pack(fill="x", pady=10)
        tk.Button(self.sidebar, text="Signout", bg="#333333", fg="white", command=self.signout).pack(fill="x", pady=10)

        # Frame principal para las vistas (stock o ventas)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Inicialmente mostrar la vista de stock
        self.current_view = "stock"
        self.setup_database()
        self.show_stock()

    def setup_database(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                codigo TEXT,
                proveedor TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                costo REAL,
                venta REAL,
                estado TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def get_db_connection(self):
        return sqlite3.connect('base.db')

    # Interfaz para gestión de stock
    def show_stock(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        input_frame = tk.LabelFrame(self.main_frame, text="Agregar Producto", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="Código:").grid(row=0, column=0, padx=5, pady=5)
        self.codigo_entry = tk.Entry(input_frame)
        self.codigo_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Proveedor:").grid(row=0, column=2, padx=5, pady=5)
        self.proveedor_entry = tk.Entry(input_frame)
        self.proveedor_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5)
        self.descripcion_entry = tk.Entry(input_frame)
        self.descripcion_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Cantidad:").grid(row=1, column=2, padx=5, pady=5)
        self.cantidad_entry = tk.Entry(input_frame)
        self.cantidad_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Costo:").grid(row=2, column=0, padx=5, pady=5)
        self.costo_entry = tk.Entry(input_frame)
        self.costo_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Venta:").grid(row=2, column=2, padx=5, pady=5)
        self.venta_entry = tk.Entry(input_frame)
        self.venta_entry.grid(row=2, column=3, padx=5, pady=5)

        tk.Button(input_frame, text="Agregar", command=self.agregar_producto).grid(row=3, column=0, columnspan=4, pady=10)

        table_frame = tk.LabelFrame(self.main_frame, text="Stock", padx=10, pady=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.stock_tree = ttk.Treeview(table_frame, columns=( "Código", "Proveedor", "Descripción", "Cantidad", "Costo", "Venta", "Estado"), show="headings")
        self.stock_tree.heading("Código", text="Código")
        self.stock_tree.heading("Proveedor", text="Proveedor")
        self.stock_tree.heading("Descripción", text="Descripción")
        self.stock_tree.heading("Cantidad", text="Cantidad")
        self.stock_tree.heading("Costo", text="Costo")
        self.stock_tree.heading("Venta", text="Venta")
        self.stock_tree.heading("Estado", text="Estado")
        self.stock_tree.pack(fill="both", expand=True)

        self.cargar_datos_stock()
        self.current_view = "stock"

    def agregar_producto(self):
        try:
            codigo = self.codigo_entry.get()
            proveedor = self.proveedor_entry.get()
            descripcion = self.descripcion_entry.get()
            cantidad = int(self.cantidad_entry.get())
            costo = float(self.costo_entry.get())
            venta = float(self.venta_entry.get())
            estado = 'Disponible' if cantidad > 0 else 'Agotado'

            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO stock (codigo, proveedor, descripcion, cantidad, costo, venta, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (codigo, proveedor, descripcion, cantidad, costo, venta, estado)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Producto cargado correctamente")
            self.limpiar_campos()
            self.cargar_datos_stock()

        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {e}")

    def limpiar_campos(self):
        self.codigo_entry.delete(0, tk.END)
        self.proveedor_entry.delete(0, tk.END)
        self.descripcion_entry.delete(0, tk.END)
        self.cantidad_entry.delete(0, tk.END)
        self.costo_entry.delete(0, tk.END)
        self.venta_entry.delete(0, tk.END)

    def cargar_datos_stock(self):
        # Limpiar tabla
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        # Cargar datos desde la base de datos
        conn = self.get_db_connection()
        df = pd.read_sql("SELECT * FROM stock", conn)
        conn.close()

        for index, row in df.iterrows():
            self.stock_tree.insert("", "end", values=(
                row['codigo'],
                row['proveedor'],
                row['descripcion'],
                row['cantidad'],
                row['costo'],
                row['venta'],
                row['estado']
            ))

    # Interfaz para ventas
    def show_sales(self):
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Frame superior (cabecera)
        header_frame = tk.Frame(self.main_frame, bg="#1ABC9C", height=50)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text=f"Bienvenido: {self.get_username()}", bg="#1ABC9C", fg="white").pack(side="left", padx=10)
        tk.Label(header_frame, text=f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", bg="#1ABC9C", fg="white").pack(side="left", padx=10)
        tk.Button(header_frame, text="Admin", bg="#666666", fg="white", command=self.admin_function).pack(side="right", padx=5)

        # Frame de búsqueda
        search_frame = tk.Frame(self.main_frame, bg="#666666", height=30)
        search_frame.pack(fill="x", pady=5)

        tk.Label(search_frame, text="Buscar por Código", bg="#666666", fg="white").pack(side="left", padx=5)
        self.search_code_entry = tk.Entry(search_frame, width=20)
        self.search_code_entry.pack(side="left", padx=5)

        tk.Label(search_frame, text="Buscar por Nombre", bg="#666666", fg="white").pack(side="left", padx=5)
        self.search_name_entry = tk.Entry(search_frame, width=20)
        self.search_name_entry.pack(side="left", padx=5)

        # Frame de la tabla de productos
        table_frame = tk.Frame(self.main_frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.sales_tree = ttk.Treeview(table_frame, columns=("#", "Artículo", "Cantidad", "Precio por Artículo", "Sub-Total"), show="headings")
        self.sales_tree.heading("#", text="#")
        self.sales_tree.heading("Artículo", text="Artículo")
        self.sales_tree.heading("Cantidad", text="Cantidad")
        self.sales_tree.heading("Precio por Artículo", text="Precio por Artículo")
        self.sales_tree.heading("Sub-Total", text="Sub-Total")
        self.sales_tree.pack(fill="both", expand=True)

        # Frame derecho (totales)
        total_frame = tk.Frame(self.main_frame, bg="#000000", width=200)
        total_frame.pack(side="right", fill="y", padx=5)

        tk.Label(total_frame, text="Sub-Total", bg="#000000", fg="white").pack(pady=5)
        self.subtotal_label = tk.Label(total_frame, text="0.00", bg="#000000", fg="white")
        self.subtotal_label.pack(pady=5)

        tk.Label(total_frame, text="Total", bg="#000000", fg="white").pack(pady=5)
        self.total_label = tk.Label(total_frame, text="0.00", bg="#000000", fg="white")
        self.total_label.pack(pady=5)

        # Frame inferior (botones)
        bottom_frame = tk.Frame(self.main_frame, bg="#666666", height=50)
        bottom_frame.pack(fill="x", pady=5)

        tk.Button(bottom_frame, text="Borrar Artículo", bg="#666666", fg="white", command=self.borrar_articulo).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Cambiar Cantidad", bg="#666666", fg="white", command=self.cambiar_cantidad).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Nueva Compra", bg="#666666", fg="white", command=self.nueva_compra).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Pagar", bg="#666666", fg="white", command=self.pagar).pack(side="right", padx=5)

        # Frame de fondo gris (puedes usar para más funciones)
        bg_frame = tk.Frame(self.main_frame, bg="#95E1D3", height=100)
        bg_frame.pack(fill="x", pady=5)

        self.current_view = "sales"

    def get_username(self):
        # Método placeholder para obtener el nombre de usuario (ajusta según tu implementación)
        return "Usuario"  # Cambia esto por la lógica real

    def admin_function(self):
        pass  # Implementa tu lógica aquí

    def signout(self):
        self.root.destroy()
        import os
        os.system("python login.py")

    def borrar_articulo(self):
        pass  # Implementa tu lógica aquí

    def cambiar_cantidad(self):
        pass  # Implementa tu lógica aquí

    def nueva_compra(self):
        pass  # Implementa tu lógica aquí

    def pagar(self):
        pass  # Implementa tu lógica aquí

def main():
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()