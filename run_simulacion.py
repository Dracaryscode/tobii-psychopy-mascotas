#!/usr/bin/env python3
"""
run_simulacion.py — Vista previa visual del experimento (sin Tobii, ventana normal).

Corre la secuencia completa con tiempos reducidos (TIEMPOS_SIMULACION) para
verificar que todos los estímulos cargan y la presentación es correcta.

Uso:
    python run_simulacion.py          # usa ID "SIM_001"
    python run_simulacion.py P01
"""

import sys

from psychopy import visual, event, core

from src import config, secuencia, tareas


# ---------------------------------------------------------------------------
# Utilidades de pantalla
# ---------------------------------------------------------------------------

def _pantalla(win, texto: str, height: float = 0.07) -> None:
    """Dibuja texto centrado y hace flip (no espera)."""
    visual.TextStim(win, text=texto, color="white", height=height, wrapWidth=1.8).draw()
    win.flip()


def _esperar_espacio(win) -> None:
    """Bloquea hasta ESPACIO. ESC sale limpiamente."""
    teclas = event.waitKeys(keyList=["space", "escape"])
    if "escape" in teclas:
        raise KeyboardInterrupt()


def _mostrar_titulo(win, texto: str, duracion: float = 2.0) -> None:
    """Muestra un título durante `duracion` segundos; ESC interrumpe."""
    stim  = visual.TextStim(win, text=texto, color="white", height=0.08)
    reloj = core.Clock()
    while reloj.getTime() < duracion:
        stim.draw()
        win.flip()
        if event.getKeys(keyList=["escape"]):
            raise KeyboardInterrupt()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(participante_id: str) -> None:
    # 1. Verificar que todas las imágenes de estímulo existen en disco
    try:
        config.verificar_estimulos()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        print("  Verifica que todas las imágenes estén en diseño_mascota/\n")
        sys.exit(1)

    # 2. Generar secuencia
    seq = secuencia.generar_secuencia(participante_id)

    # 3. Abrir ventana PsychoPy (modo ventana, no pantalla completa)
    win = visual.Window(
        fullscr=False,
        color="gray",
        units="norm",
        title="Simulación - Proyecto Mascotas",
    )

    try:
        # 4. Bienvenida
        _pantalla(
            win,
            "SIMULACIÓN - Proyecto Mascotas\n\n"
            "Tarea 1: 36 ensayos  |  Tarea 2: 24 ensayos\n\n"
            "Presiona ESPACIO para comenzar",
        )
        _esperar_espacio(win)

        # 5. Tarea 1
        _mostrar_titulo(win, "TAREA 1 - Comparación de características")
        tareas.correr_tarea1(win, seq, config.TIEMPOS_SIMULACION)

        # 6. Pausa entre tareas
        _pantalla(win, "Pausa.\n\nPresiona ESPACIO para continuar con Tarea 2.")
        _esperar_espacio(win)

        # 7. Tarea 2
        _mostrar_titulo(win, "TAREA 2 - Variantes completas")
        tareas.correr_tarea2(win, seq, config.TIEMPOS_SIMULACION)

        # 8. Fin
        _pantalla(win, "Simulación completada.\n\nPresiona cualquier tecla para cerrar.")
        event.waitKeys()

    except KeyboardInterrupt:
        visual.TextStim(win, text="Saliendo...", color="white", height=0.1).draw()
        win.flip()
        core.wait(0.8)

    finally:
        win.close()


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else "SIM_001"
    main(pid)
