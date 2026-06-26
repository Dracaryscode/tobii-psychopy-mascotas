#!/usr/bin/env python3
"""
generar_placeholders.py — Crea imágenes de marcador de posición (placeholders).

Genera PNGs simples con el nombre de cada estímulo, para que el experimento real
pueda ejecutarse y probarse ANTES de tener el arte final.
Reemplaza estos archivos por las imágenes reales de las mascotas (mismos nombres).

Uso:
    python generar_placeholders.py
"""

from PIL import Image, ImageDraw, ImageFont

from src import config


COLORES = {
    "tarea1": (120, 160, 200),
    "tarea2": (200, 160, 120),
    "tarea3": (140, 190, 150),
}


def _crear(ruta, texto, color, tamano=(600, 600)):
    img = Image.new("RGB", tamano, color)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    # Centrar el texto
    bbox = d.textbbox((0, 0), texto, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((tamano[0]-w)/2, (tamano[1]-h)/2), texto, fill="white", font=font)
    d.rectangle([0, 0, tamano[0]-1, tamano[1]-1], outline="white", width=4)
    img.save(ruta)


def main():
    config.preparar_directorios()
    n = 0

    for nombre, archivo in config.MASCOTAS_T1.items():
        _crear(config.ESTIMULOS_DIR / "tarea1" / archivo, nombre, COLORES["tarea1"])
        n += 1

    for grupo, niveles in config.GRUPOS_T2.items():
        for nombre, archivo in niveles.items():
            _crear(config.ESTIMULOS_DIR / "tarea2" / archivo,
                   f"{grupo}\n{nombre}", COLORES["tarea2"], (500, 500))
            n += 1

    for nombre, archivo in config.VARIANTES_T3.items():
        _crear(config.ESTIMULOS_DIR / "tarea3" / archivo, nombre, COLORES["tarea3"], (420, 420))
        n += 1

    print(f"✓ {n} placeholders generados en {config.ESTIMULOS_DIR}")
    print("  Reemplázalos por las imágenes reales (mismos nombres de archivo).")


if __name__ == "__main__":
    main()
