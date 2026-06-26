"""
tareas.py — Rutinas de presentación de las tareas (PsychoPy, units=norm).

Tarea 1 y Tarea 2: comparación pairwise — dos imágenes lado a lado.

Flujo de cada ensayo:
    1. Cruz de fijación  (tiempos[tarea]["fijacion_s"])
    2. Par de imágenes   (tiempos[tarea]["visualizacion_s"])  — ESPACIO avanza

Ambas funciones reciben el dict completo de tiempos (con claves "tarea1"/"tarea2")
para ser compatibles tanto con config.TIEMPOS como con config.TIEMPOS_SIMULACION.
"""

from psychopy import visual, event, core


# ---------------------------------------------------------------------------
# Constantes de layout (norm units)
# ---------------------------------------------------------------------------
_SIZE_IMG = (0.80, 0.90)
_POS_IZQ  = (-0.48, 0)
_POS_DER  = ( 0.48, 0)

# Rect de fondo: SIZE + 0.06 en cada dimensión para que asomen ligeramente
_FONDO_W = 0.86
_FONDO_H = 0.96


def _hacer_imagen(win, ruta, pos, size):
    """Crea un ImageStim nuevo con size/pos/units en el constructor.
    PsychoPy cachea las texturas de disco internamente."""
    return visual.ImageStim(
        win,
        image=str(ruta),
        pos=pos,
        size=size,
        units="norm",
    )


def _mostrar_por(win, segundos: float, drawables: list, avanzar: bool = False) -> None:
    """
    Dibuja `drawables` en bucle durante `segundos`.
    ESC  → KeyboardInterrupt (cierra el experimento).
    SPACE → sale del bucle anticipadamente si avanzar=True.
    """
    reloj = core.Clock()
    while reloj.getTime() < segundos:
        for d in drawables:
            d.draw()
        win.flip()
        teclas = event.getKeys(keyList=["escape", "space"])
        if "escape" in teclas:
            raise KeyboardInterrupt("Experimento abortado (ESC).")
        if avanzar and "space" in teclas:
            break


# ---------------------------------------------------------------------------
# Tarea 1 — comparación pairwise
# ---------------------------------------------------------------------------
def correr_tarea1(win, secuencia: dict, tiempos: dict, registro=None) -> None:
    """
    Presenta los ensayos de Tarea 1 (dos imágenes lado a lado).

    secuencia : dict completo de generar_secuencia()
    tiempos   : config.TIEMPOS o config.TIEMPOS_SIMULACION
    registro  : RegistroParticipante opcional; si es None, no se guarda nada
    """
    ensayos = secuencia["tarea1"]
    t       = tiempos["tarea1"]
    total   = len(ensayos)

    cruz  = visual.TextStim(win, text="+", color="black", height=0.1, bold=True)
    ayuda = visual.TextStim(win, text="", color="gray",  height=0.04, pos=(0, -0.9))

    # Rectángulos de fondo — creados una sola vez, reutilizados en cada ensayo
    fondo_izq = visual.Rect(
        win, width=_FONDO_W, height=_FONDO_H,
        pos=_POS_IZQ, fillColor="white", lineColor=None,
        units="norm",
    )
    fondo_der = visual.Rect(
        win, width=_FONDO_W, height=_FONDO_H,
        pos=_POS_DER, fillColor="white", lineColor=None,
        units="norm",
    )

    reloj_reg = core.Clock()

    for ensayo in ensayos:
        n = ensayo["ensayo"]
        ayuda.text = f"Ensayo {n}/{total}"

        # --- Fijación ---
        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea1", "fijacion_on",
                n_ensayo=n, repeticion=ensayo["repeticion"],
                grupo=ensayo["grupo"],
            )
        _mostrar_por(win, t["fijacion_s"], [cruz, ayuda])

        # --- Comparación ---
        img_izq = _hacer_imagen(win, ensayo["imagen_izq"], pos=_POS_IZQ, size=_SIZE_IMG)
        img_der = _hacer_imagen(win, ensayo["imagen_der"], pos=_POS_DER, size=_SIZE_IMG)

        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea1", "imagen_on",
                n_ensayo=n, repeticion=ensayo["repeticion"],
                grupo=ensayo["grupo"],
                estimulo=f"{ensayo['nombre_izq']} | {ensayo['nombre_der']}",
                posicion="izquierda | derecha",
            )
        _mostrar_por(
            win, t["visualizacion_s"],
            [fondo_izq, fondo_der, img_izq, img_der],
            avanzar=True,
        )

        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea1", "imagen_off",
                n_ensayo=n, repeticion=ensayo["repeticion"],
            )


# ---------------------------------------------------------------------------
# Tarea 2 — comparación pairwise (misma estructura visual que Tarea 1)
# ---------------------------------------------------------------------------
def correr_tarea2(win, secuencia: dict, tiempos: dict, registro=None) -> None:
    """
    Presenta los ensayos de Tarea 2 (dos imágenes lado a lado).

    secuencia : dict completo de generar_secuencia()
    tiempos   : config.TIEMPOS o config.TIEMPOS_SIMULACION
    registro  : RegistroParticipante opcional; si es None, no se guarda nada
    """
    ensayos = secuencia["tarea2"]
    t       = tiempos["tarea2"]
    total   = len(ensayos)

    cruz  = visual.TextStim(win, text="+", color="black", height=0.1, bold=True)
    ayuda = visual.TextStim(win, text="", color="gray",  height=0.04, pos=(0, -0.9))

    # Rectángulos de fondo — creados una sola vez, reutilizados en cada ensayo
    fondo_izq = visual.Rect(
        win, width=_FONDO_W, height=_FONDO_H,
        pos=_POS_IZQ, fillColor="white", lineColor=None,
        units="norm",
    )
    fondo_der = visual.Rect(
        win, width=_FONDO_W, height=_FONDO_H,
        pos=_POS_DER, fillColor="white", lineColor=None,
        units="norm",
    )

    reloj_reg = core.Clock()

    for ensayo in ensayos:
        n = ensayo["ensayo"]
        ayuda.text = f"Ensayo {n}/{total}"

        # --- Fijación ---
        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea2", "fijacion_on",
                n_ensayo=n, repeticion=ensayo["repeticion"],
            )
        _mostrar_por(win, t["fijacion_s"], [cruz, ayuda])

        # --- Comparación ---
        img_izq = _hacer_imagen(win, ensayo["imagen_izq"], pos=_POS_IZQ, size=_SIZE_IMG)
        img_der = _hacer_imagen(win, ensayo["imagen_der"], pos=_POS_DER, size=_SIZE_IMG)

        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea2", "imagen_on",
                n_ensayo=n, repeticion=ensayo["repeticion"],
                estimulo=f"{ensayo['nombre_izq']} | {ensayo['nombre_der']}",
                posicion="izquierda | derecha",
            )
        _mostrar_por(
            win, t["visualizacion_s"],
            [fondo_izq, fondo_der, img_izq, img_der],
            avanzar=True,
        )

        if registro:
            registro.log(
                reloj_reg.getTime(), "tarea2", "imagen_off",
                n_ensayo=n, repeticion=ensayo["repeticion"],
            )
