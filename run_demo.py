#!/usr/bin/env python3
"""
run_demo.py — Vista previa visual con PsychoPy, SIN Tobii ni guardado de datos.

Muestra los primeros N ensayos de cada tarea para verificar:
  - Que las imágenes cargan y se ven bien en pantalla.
  - Que la cruz de fijación, los tiempos y las instrucciones funcionan.
  - El flujo general del experimento.

No requiere el Tobii Pro Fusion conectado.
No guarda ningún dato en disco.

Uso:
    python run_demo.py            # 3 ensayos por tarea
    python run_demo.py 5          # 5 ensayos por tarea
    python run_demo.py full       # secuencia completa (36 + 16 ensayos)
"""

import sys

# --- Mock del tracker ANTES de que tareas.py lo importe --------------------
import src.tracker as _tk

class _MockIO:
    def sendMessageEvent(self, **kw): pass
    def quit(self): pass

class _MockTracker:
    def setRecordingState(self, state): pass
    def runSetupProcedure(self): pass

_mock_io      = _MockIO()
_mock_tracker = _MockTracker()

_tk.iniciar           = lambda *a, **kw: (_mock_io, _mock_tracker)
_tk.calibrar          = lambda *a: None
_tk.iniciar_grabacion = lambda *a: None
_tk.detener_grabacion = lambda *a: None
_tk.marcador          = lambda *a: None
_tk.cerrar            = lambda *a: None

# --- Imports normales -------------------------------------------------------
from psychopy import core

from src import config, secuencia, pantallas
from src import tareas


class _RegistroMock:
    """Registro que no escribe nada a disco."""
    n_eventos = 0
    def log(self, *a, **kw): pass
    def log_ensayo(self, *a, **kw): pass
    def iniciar(self): pass
    def cerrar(self): pass


def main(n_ensayos: int | None) -> None:
    config.preparar_directorios()
    secuencias = secuencia.construir_todo("DEMO")

    if n_ensayos is not None:
        for k in secuencias:
            secuencias[k] = secuencias[k][:n_ensayos]
            # Re-numerar para que los índices sean coherentes
            for i, e in enumerate(secuencias[k], 1):
                e["n_ensayo"] = i

    reloj   = core.Clock()
    win     = pantallas.crear_ventana()
    registro = _RegistroMock()

    sufijo = f"({n_ensayos} por tarea)" if n_ensayos else "(secuencia completa)"
    print(f"\n  DEMO {sufijo}  —  ESC para salir en cualquier momento\n")

    try:
        pantallas.mostrar_texto(
            win,
            "MODO DEMO — sin Tobii, sin guardado de datos\n\n"
            f"Tarea 1: {len(secuencias['tarea1'])} ensayos\n"
            f"Tarea 2: {len(secuencias['tarea2'])} ensayos\n\n"
            "Pulsa ESPACIO para empezar."
        )

        # --- Tarea 1 ---
        tareas.ejecutar_tarea(win, _mock_io, secuencias["tarea1"], registro, reloj)
        pantallas.mostrar_texto(win, pantallas.INSTRUCCIONES["pausa"])

        # --- Tarea 2 ---
        tareas.ejecutar_tarea(win, _mock_io, secuencias["tarea2"], registro, reloj)

        pantallas.mostrar_texto(win, pantallas.INSTRUCCIONES["fin"])

    except KeyboardInterrupt:
        print("  Demo detenida por el operador (ESC).")
    finally:
        win.close()
        core.quit()


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "3"
    n = None if arg.lower() == "full" else int(arg)
    main(n)
