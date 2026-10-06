"""Interfaz gráfica moderna de SIGEAH construida con customtkinter."""

import sqlite3
from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from app.database import actualizar_estado, conectar, inicializar_db
from app.emergencia import listar_emergencias, registrar_emergencia
from app.validaciones import ESTADOS, PRIORIDADES, TIPOS_EMERGENCIA

TODOS = "todos"
COLUMNAS = ("ID", "Título", "Tipo", "Ubicación", "Fecha", "Prioridad", "Estado")
ANCHOS = (40, 200, 90, 180, 130, 80, 90)
PESTANA_REGISTRO = "Registrar emergencia"
PESTANA_CONSULTA = "Consultar y actualizar"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class VentanaSigeah(ctk.CTk):
    """Ventana principal de SIGEAH con las pestañas de registro y consulta."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        """Crea la ventana y sus pestañas.

        Args:
            conexion: Conexión SQLite abierta.
        """
        super().__init__()
        self.title("SIGEAH - Sistema de Gestión de Emergencias")
        self.geometry("1000x580")
        self.conexion = conexion

        ctk.CTkLabel(
            self, text="🚨 SIGEAH", font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(15, 0))

        pestanas = ctk.CTkTabview(self)
        pestanas.pack(fill="both", expand=True, padx=15, pady=15)
        self.pestana_registro = pestanas.add(PESTANA_REGISTRO)
        self.pestana_consulta = pestanas.add(PESTANA_CONSULTA)

        self._configurar_tabla_estilo()
        self._crear_registro()
        self._crear_consulta()
        self.consultar()

    @staticmethod
    def _configurar_tabla_estilo() -> None:
        """Ajusta el aspecto de la tabla para que combine con el tema."""
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        estilo.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#1f6aa5",
            foreground="white",
        )

    # ---------- Pestaña: registrar ----------

    def _crear_registro(self) -> None:
        """Construye el formulario de registro."""
        marco = self.pestana_registro
        marco.columnconfigure(1, weight=1)
        definiciones = (
            ("titulo", "Título", None),
            ("tipo", "Tipo", TIPOS_EMERGENCIA),
            ("descripcion", "Descripción", None),
            ("ubicacion", "Ubicación", None),
            ("fecha", "Fecha y hora (AAAA-MM-DD HH:MM)", None),
            ("prioridad", "Prioridad", PRIORIDADES),
            ("estado", "Estado", ESTADOS),
        )
        self.campos = {}
        for fila, (clave, etiqueta, opciones) in enumerate(definiciones):
            ctk.CTkLabel(marco, text=etiqueta).grid(
                row=fila, column=0, sticky="w", padx=10, pady=6
            )
            if opciones:
                widget = ctk.CTkComboBox(marco, values=list(opciones), state="readonly")
            else:
                widget = ctk.CTkEntry(marco)
            widget.grid(row=fila, column=1, sticky="ew", padx=10, pady=6)
            self.campos[clave] = widget
        ctk.CTkButton(marco, text="Registrar emergencia", command=self.registrar).grid(
            row=len(definiciones), column=1, sticky="e", padx=10, pady=14
        )
        self._limpiar_formulario()

    def _limpiar_formulario(self) -> None:
        """Restablece el formulario a sus valores por defecto."""
        ahora = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        por_defecto = {
            "tipo": "otro",
            "prioridad": "media",
            "estado": "pendiente",
            "fecha": ahora,
        }
        for clave, widget in self.campos.items():
            if isinstance(widget, ctk.CTkComboBox):
                widget.set(por_defecto[clave])
            else:
                widget.delete(0, "end")
                if clave in por_defecto:
                    widget.insert(0, por_defecto[clave])

    def registrar(self) -> None:
        """Valida y guarda la emergencia escrita en el formulario."""
        datos = {clave: widget.get() for clave, widget in self.campos.items()}
        try:
            emergencia = registrar_emergencia(self.conexion, datos)
        except (ValueError, TypeError) as error:
            messagebox.showwarning("Datos inválidos", str(error))
            return
        except RuntimeError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo(
            "Emergencia registrada", f"Emergencia registrada con ID {emergencia.id}."
        )
        self._limpiar_formulario()
        self.consultar()

    # ---------- Pestaña: consultar y actualizar ----------

    def _crear_consulta(self) -> None:
        """Construye filtros, tabla y control de cambio de estado."""
        marco = self.pestana_consulta
        filtros = ctk.CTkFrame(marco, fg_color="transparent")
        filtros.pack(fill="x")

        self.busqueda = ctk.CTkEntry(
            filtros, width=200, placeholder_text="Buscar título o ubicación"
        )
        self.busqueda.pack(side="left", padx=(0, 10))

        self.combos_filtro = {}
        for nombre, opciones in (
            ("tipo", TIPOS_EMERGENCIA),
            ("estado", ESTADOS),
            ("prioridad", PRIORIDADES),
        ):
            combo = ctk.CTkComboBox(
                filtros, values=[TODOS, *opciones], state="readonly", width=120
            )
            combo.set(TODOS)
            combo.pack(side="left", padx=(0, 10))
            self.combos_filtro[nombre] = combo

        ctk.CTkButton(filtros, text="Buscar", width=80, command=self.consultar).pack(
            side="left"
        )
        ctk.CTkButton(
            filtros,
            text="Limpiar",
            width=80,
            fg_color="gray",
            command=self.limpiar_filtros,
        ).pack(side="left", padx=8)

        contenedor = ctk.CTkFrame(marco)
        contenedor.pack(fill="both", expand=True, pady=12)
        self.tabla = ttk.Treeview(
            contenedor, columns=COLUMNAS, show="headings", height=12
        )
        for columna, ancho in zip(COLUMNAS, ANCHOS):
            self.tabla.heading(columna, text=columna)
            self.tabla.column(columna, width=ancho)
        self.tabla.tag_configure("alta", foreground="#c0392b")
        self.tabla.tag_configure("media", foreground="#b9770e")
        self.tabla.tag_configure("baja", foreground="#1e8449")
        self.tabla.pack(fill="both", expand=True, padx=4, pady=4)

        pie = ctk.CTkFrame(marco, fg_color="transparent")
        pie.pack(fill="x")
        ctk.CTkLabel(pie, text="Nuevo estado de la fila seleccionada:").pack(
            side="left"
        )
        self.nuevo_estado = ctk.CTkComboBox(
            pie, values=list(ESTADOS), state="readonly", width=130
        )
        self.nuevo_estado.set(ESTADOS[1])
        self.nuevo_estado.pack(side="left", padx=10)
        ctk.CTkButton(pie, text="Aplicar cambio", command=self.cambiar_estado).pack(
            side="left"
        )

    def limpiar_filtros(self) -> None:
        """Quita la búsqueda y los filtros, y recarga la tabla."""
        self.busqueda.delete(0, "end")
        for combo in self.combos_filtro.values():
            combo.set(TODOS)
        self.consultar()

    def consultar(self) -> None:
        """Carga en la tabla las emergencias que cumplen búsqueda y filtros."""

        def valor(nombre: str) -> str | None:
            elegido = self.combos_filtro[nombre].get()
            return None if elegido == TODOS else elegido

        try:
            emergencias = listar_emergencias(
                self.conexion,
                texto=self.busqueda.get(),
                tipo=valor("tipo"),
                estado=valor("estado"),
                prioridad=valor("prioridad"),
            )
        except RuntimeError as error:
            messagebox.showerror("Error", str(error))
            return
        self.tabla.delete(*self.tabla.get_children())
        for e in emergencias:
            self.tabla.insert(
                "",
                "end",
                iid=str(e.id),
                values=(
                    e.id,
                    e.titulo,
                    e.tipo,
                    e.ubicacion,
                    e.fecha,
                    e.prioridad,
                    e.estado,
                ),
                tags=(e.prioridad,),
            )

    def cambiar_estado(self) -> None:
        """Cambia el estado de la emergencia seleccionada en la tabla."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Seleccione una fila", "Elija primero una emergencia.")
            return
        try:
            actualizar_estado(self.conexion, seleccion[0], self.nuevo_estado.get())
        except (ValueError, TypeError) as error:
            messagebox.showwarning("No se pudo actualizar", str(error))
            return
        except sqlite3.Error:
            self.conexion.rollback()
            messagebox.showerror("Error", "No se pudo guardar el cambio.")
            return
        messagebox.showinfo("Listo", "Estado actualizado.")
        self.consultar()


def main() -> None:
    """Abre la base de datos y lanza la interfaz gráfica."""
    conexion = conectar()
    try:
        inicializar_db(conexion)
        VentanaSigeah(conexion).mainloop()
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
