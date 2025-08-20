import os
import io
import requests
import ttkbootstrap as tb
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from plyer import notification

# --- Configuración ---
CARPETA_DESCARGAS = os.path.join(os.getcwd(), "Mis Imágenes Descargadas")
os.makedirs(CARPETA_DESCARGAS, exist_ok=True)  # Crear carpeta si no existe

# --- Funciones ---
def actualizar_progreso(valor):
    barra["value"] = valor
    ventana.update_idletasks()

def descargar_imagen():
    url = entrada_url.get().strip()
    if not url:
        messagebox.showwarning("Advertencia", "Por favor ingresa una URL de imagen.")
        return

    formato = combo_formato.get().lower() or "jpg"

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        response.raise_for_status()

        # --- Validar si la URL realmente devuelve una imagen ---
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            messagebox.showerror(
                "Error",
                f"La URL no apunta a una imagen directa.\n\nContent-Type recibido: {content_type}\n\n"
                "👉 Consejo: abre el enlace en el navegador, haz clic derecho sobre la imagen y selecciona "
                "'Copiar dirección de la imagen'."
            )
            return

        # Progreso por chunks
        total = int(response.headers.get("content-length", 0))
        data = io.BytesIO()
        descargado = 0
        for chunk in response.iter_content(1024):
            if chunk:
                data.write(chunk)
                descargado += len(chunk)
                if total > 0:
                    actualizar_progreso(int(descargado * 100 / total))

        img = Image.open(io.BytesIO(data.getvalue()))

        nombre_base = os.path.basename(url.split("?")[0])
        if "." in nombre_base:
            nombre_base = os.path.splitext(nombre_base)[0]
        archivo = os.path.join(CARPETA_DESCARGAS, f"{nombre_base}.{formato}")

        contador = 1
        while os.path.exists(archivo):
            archivo = os.path.join(CARPETA_DESCARGAS, f"{nombre_base}_{contador}.{formato}")
            contador += 1

        img.save(archivo, formato.upper())
        mostrar_preview(img)

        notification.notify(
            title="✅ Imagen descargada",
            message=f"Guardada en:\n{archivo}",
            timeout=5
        )
        messagebox.showinfo("Éxito", f"Imagen descargada en:\n{archivo}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar la imagen:\n{e}")
    finally:
        actualizar_progreso(0)

def convertir_enc():
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo .enc",
        filetypes=[("Archivos .enc", "*.enc"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return

    try:
        with open(ruta, "rb") as f:
            data = f.read()

        # Simular proceso en 3 pasos
        actualizar_progreso(30)
        img = Image.open(io.BytesIO(data))
        actualizar_progreso(60)

        nombre_base = os.path.splitext(os.path.basename(ruta))[0]
        archivo = os.path.join(CARPETA_DESCARGAS, f"{nombre_base}.jpg")

        contador = 1
        while os.path.exists(archivo):
            archivo = os.path.join(CARPETA_DESCARGAS, f"{nombre_base}_{contador}.jpg")
            contador += 1

        img.save(archivo, "JPEG")
        mostrar_preview(img)

        actualizar_progreso(100)

        notification.notify(
            title="✅ Conversión completa",
            message=f"Imagen guardada en:\n{archivo}",
            timeout=5
        )
        messagebox.showinfo("Éxito", f"Imagen convertida en:\n{archivo}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir el archivo:\n{e}")
    finally:
        actualizar_progreso(0)

def mostrar_preview(img):
    try:
        img.thumbnail((250, 250))
        foto = ImageTk.PhotoImage(img)
        lbl_preview.config(image=foto, text="")
        lbl_preview.image = foto
    except:
        lbl_preview.config(text="No se pudo mostrar vista previa")

def descargar_facebook():
    url = entrada_url.get().strip()
    if "facebook" not in url and "fbcdn" not in url:
        messagebox.showwarning("Advertencia", "La URL no parece ser de Facebook.")
        return
    descargar_imagen()

# --- Interfaz ---
ventana = tb.Window(themename="superhero")
ventana.title("📥 Descargador y Convertidor de Imágenes Pro")
ventana.geometry("560x560")
ventana.resizable(False, False)

titulo = tb.Label(
    ventana,
    text="📥 Descargador y Convertidor de Imágenes Pro",
    font=("Segoe UI", 16, "bold"),
    bootstyle="info"
)
titulo.pack(pady=15)

frame = tb.Frame(ventana)
frame.pack(pady=10)

tb.Label(frame, text="URL de la imagen:", font=("Segoe UI", 11)).pack(anchor="w")
entrada_url = tb.Entry(frame, width=55, bootstyle="info")
entrada_url.pack(pady=5)

tb.Label(frame, text="Formato de descarga:", font=("Segoe UI", 11)).pack(anchor="w", pady=5)
combo_formato = tb.Combobox(frame, values=["JPG", "PNG", "WEBP"], bootstyle="success")
combo_formato.set("JPG")
combo_formato.pack(pady=5)

btn_descargar = tb.Button(
    ventana,
    text="⬇ Descargar Imagen desde URL",
    bootstyle="success-outline",
    command=descargar_imagen,
    width=30
)
btn_descargar.pack(pady=10)

btn_enc = tb.Button(
    ventana,
    text="📂 Subir .enc y Convertir a JPG",
    bootstyle="warning-outline",
    command=convertir_enc,
    width=30
)
btn_enc.pack(pady=5)

btn_fb = tb.Button(
    ventana,
    text="⬇ Descargar Imagen de Facebook",
    bootstyle="primary-outline",
    command=descargar_facebook,
    width=30
)
btn_fb.pack(pady=5)

# Barra de progreso
barra = tb.Progressbar(
    ventana,
    bootstyle="success-striped",
    length=400,
    mode="determinate"
)
barra.pack(pady=15)

lbl_preview = tb.Label(ventana, text="Vista previa aparecerá aquí", bootstyle="secondary")
lbl_preview.pack(pady=10)

tb.Label(
    ventana,
    text=f"📂 Carpeta de descargas: {CARPETA_DESCARGAS}",
    font=("Segoe UI", 9),
    bootstyle="secondary"
).pack(side="bottom", pady=10)

ventana.mainloop()
