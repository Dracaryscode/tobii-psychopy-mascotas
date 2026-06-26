#!/usr/bin/env python3
"""
run_experimento.py — EJECUTAR CON EL PARTICIPANTE REAL.

Requisitos: PsychoPy + tobii_research instalados, Tobii Pro Fusion conectado.

Flujo:
    1. Verifica que el ID no tenga datos previos (los participantes no repiten).
    2. Bienvenida → calibración Tobii.
    3. Tarea 1 (36 ensayos) → pausa → Tarea 2 (16 ensayos).
    4. Graba la mirada en HDF5 (ioHub) + eventos en CSV (escritura inmediata).

Uso:
    python run_experimento.py
    python run_experimento.py P01
"""

import sys

from psychopy import core

from src import config, secuencia
from src import registro as reg
from src import pantallas
from src import tracker as tk
from src import tareas


def main(participante: str) -> None:
    config.preparar_directorios()

    registro = reg.RegistroParticipante(participante)

    # --- Guarda contra duplicado (ANTES de abrir la ventana) ----------------`source venv311/bin/activate && python run_demo.py 3`
    try:
        registro.verificar_no_duplicado()
    except ValueError as e:
        print(e)
        sys.exit(1)

    # --- Construir secuencias ------------------------------------------------
    secuencias = secuencia.construir_todo(participante)

    reloj = core.Clock()
    win   = pantallas.crear_ventana()
    io    = None

    try:
        registro.iniciar()

        # --- Bienvenida ---
        pantallas.mostrar_texto(win, pantallas.INSTRUCCIONES["bienvenida"])

        # --- Tobii: conectar + calibrar ---
        io, tracker = tk.iniciar(participante, registro.ruta_hdf5)
        registro.log(reloj.getTime(), "setup", "calibracion_inicio")
        tk.calibrar(tracker)
        registro.log(reloj.getTime(), "setup", "calibracion_fin")

        # --- Grabación ON ---
        tk.iniciar_grabacion(tracker)
        tk.marcador(io, f"INICIO|participante={participante}")
        registro.log(reloj.getTime(), "setup", "grabacion_inicio",
                     extra={"participante": participante})

        # --- Tarea 1 ---
        tareas.ejecutar_tarea(win, io, secuencias["tarea1"], registro, reloj)
        registro.log(reloj.getTime(), "tarea1", "fin_tarea")

        pantallas.mostrar_texto(win, pantallas.INSTRUCCIONES["pausa"])
        registro.log(reloj.getTime(), "pausa", "pausa")

        # --- Tarea 2 ---
        tareas.ejecutar_tarea(win, io, secuencias["tarea2"], registro, reloj)
        registro.log(reloj.getTime(), "tarea2", "fin_tarea")

        # --- Cierre ---
        tk.marcador(io, f"FIN|participante={participante}")
        tk.detener_grabacion(tracker)
        registro.log(reloj.getTime(), "fin", "grabacion_fin")

        pantallas.mostrar_texto(win, pantallas.INSTRUCCIONES["fin"])

    except KeyboardInterrupt:
        print("\n  Experimento abortado por el operador (ESC).")
        if registro._fh:
            registro.log(reloj.getTime(), "fin", "abortado")
    finally:
        registro.log(reloj.getTime(), "fin", "cierre")
        registro.cerrar()
        tk.cerrar(io)
        win.close()
        core.quit()

    print(f"\n  Eventos: {registro.ruta_csv}  ({registro.n_eventos} filas)")
    print(f"  Mirada:  {registro.ruta_hdf5}")


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else input("ID del participante: ").strip()
    if not pid:
        sys.exit("Debes indicar un ID de participante.")
    main(pid)
