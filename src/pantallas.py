"""
pantallas.py — Pantallas auxiliares: instrucciones, fijación, pausas.

Requiere PsychoPy (sólo se importa en el runner real, no en la simulación).
"""

from psychopy import visual, event, core

from . import config


def crear_ventana():
    return visual.Window(
        size=config.PANTALLA_RESOLUCION,
        fullscr=config.PANTALLA_FULLSCREEN,
        color=config.PANTALLA_COLOR_FONDO,
        units="pix",
        monitor=config.MONITOR_NOMBRE,
        allowGUI=False,
    )


def cruz_fijacion(win):
    sz = config.FIJACION_TAMANO_PX / 2
    return visual.ShapeStim(
        win,
        vertices=((0, -sz), (0, sz), (0, 0), (-sz, 0), (sz, 0)),
        lineWidth=4,
        closeShape=False,
        lineColor=config.FIJACION_COLOR,
    )


def mostrar_texto(win, texto, esperar_tecla=True):
    stim = visual.TextStim(
        win, text=texto, color="white", height=32,
        wrapWidth=config.PANTALLA_RESOLUCION[0] * 0.8,
    )
    stim.draw()
    win.flip()
    if esperar_tecla:
        teclas = event.waitKeys(keyList=[config.TECLA_AVANZAR, config.TECLA_SALIR])
        if config.TECLA_SALIR in teclas:
            raise KeyboardInterrupt("Experimento abortado por el operador.")


def mostrar_por(win, segundos, dibujar=None):
    """
    Mantiene la pantalla durante `segundos`, refrescando cada frame.
    `dibujar` es una función sin argumentos que dibuja los estímulos.
    """
    reloj = core.Clock()
    while reloj.getTime() < segundos:
        if dibujar:
            dibujar()
        win.flip()
        if event.getKeys(keyList=[config.TECLA_SALIR]):
            raise KeyboardInterrupt("Experimento abortado por el operador.")


# ---------------------------------------------------------------------------
# Textos de instrucciones
# ---------------------------------------------------------------------------
INSTRUCCIONES = {
    "bienvenida": (
        "Bienvenido/a al estudio.\n\n"
        "Verás una serie de imágenes en la pantalla.\n"
        "Solo míralas con naturalidad, sin hacer nada más.\n\n"
        "Primero realizaremos la calibración del equipo.\n\n"
        "Pulsa ESPACIO para comenzar."
    ),
    "tarea1": (
        "PARTE 1\n\n"
        "Verás imágenes de una mascota, una por una.\n"
        "Obsérvalas con naturalidad.\n\n"
        "Pulsa ESPACIO para empezar."
    ),
    "tarea2": (
        "PARTE 2\n\n"
        "Verás versiones completas de la mascota, una por una.\n"
        "Obsérvalas con naturalidad.\n\n"
        "Pulsa ESPACIO para empezar."
    ),
    "pausa": (
        "Pausa breve.\n\n"
        "Descansa un momento.\n"
        "Cuando estés listo/a, pulsa ESPACIO para continuar."
    ),
    "fin": (
        "¡Hemos terminado!\n\n"
        "Muchas gracias por tu participación.\n\n"
        "Pulsa ESPACIO para salir."
    ),
}
