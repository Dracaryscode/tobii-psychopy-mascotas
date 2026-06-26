"""
tracker.py — Conexión, calibración y grabación con el Tobii Pro Fusion.

Usa PsychoPy ioHub, que envuelve el Tobii Pro SDK (paquete `tobii_research`).
ioHub graba TODA la mirada a un archivo HDF5 mientras la grabación está activa,
y permite enviar "marcadores" (message events) que quedan en el mismo reloj que
la mirada — eso es lo que luego usas para segmentar por ensayo.

⚠️ Este módulo SÍ requiere PsychoPy + tobii_research instalados y el equipo
   conectado. No se importa en la simulación ni en los tests.
"""

from psychopy.iohub import launchHubServer

from . import config


def iniciar(participante: str, ruta_hdf5):
    """
    Lanza el servidor ioHub con el Tobii configurado.
    Devuelve (io, tracker).
    """
    iohub_config = {
        "eyetracker.hw.tobii.EyeTracker": {
            "name": "tracker",
            "runtime_settings": {"sampling_rate": config.TASA_MUESTREO_HZ},
        },
        # ioHub guarda la mirada en este HDF5:
        "experiment_code": "mascotas",
        "session_code": participante,
        "datastore_name": str(ruta_hdf5.with_suffix("")),  # ioHub añade .hdf5
    }
    io = launchHubServer(**iohub_config)
    tracker = io.getDevice("tracker")
    return io, tracker


def calibrar(tracker):
    """Lanza la rutina de calibración integrada de ioHub (9 puntos)."""
    return tracker.runSetupProcedure()


def iniciar_grabacion(tracker):
    tracker.setRecordingState(True)


def detener_grabacion(tracker):
    tracker.setRecordingState(False)


def marcador(io, texto: str):
    """Envía un marcador temporal a la grabación (queda en el reloj de la mirada)."""
    io.sendMessageEvent(text=texto, category="EXP")


def mirada_actual(tracker):
    """Posición de mirada más reciente (x, y) o None. Útil para verificación en vivo."""
    return tracker.getLastGazePosition()


def cerrar(io):
    if io is not None:
        io.quit()
