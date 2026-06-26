"""
config.py — Configuración del experimento de mascotas.

DISEÑO (2 tareas):
    Tarea 1 — Comparación pairwise de características (3 grupos × C(3,2)=3 pares)
        4 repeticiones del bloque pseudoaleatorizado = 36 ensayos
        Cada ensayo: cruz 1 s → dos imágenes lado a lado 10 s

    Tarea 2 — Totalidad: 4 variantes simultáneas en cuadrícula 2×2
        4 disposiciones (cuadrado latino 4×4) × 4 repeticiones = 16 ensayos
        Cada ensayo: cruz 1 s → cuadrícula 10 s
"""

from pathlib import Path

# =============================================================================
# RUTAS
# =============================================================================
RUTA_BASE  = Path(__file__).parent.parent
RUTA_DATOS = RUTA_BASE / "datos"
DATOS_DIR  = RUTA_DATOS   # alias usado por registro.py

# =============================================================================
# ESTÍMULOS — TAREA 1
# Estructura: {grupo: {variante: Path}}
# =============================================================================
ESTIMULOS_T1 = {
    "Ojos": {
        "pequeño": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Ojos" / "T1_ojos_pequeño.png",
        "control": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Ojos" / "T1_ojos_control.png",
        "grandes": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Ojos" / "T1_ojos_grandes.png",
    },
    "Cabeza": {
        "control": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Cabeza" / "T1_cabeza_control.png",
        "grande":  RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Cabeza" / "T1_cabeza_grande.png",
        "pequeña": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Cabeza" / "T1_cabeza_pequeña.png",
    },
    "Triángulo": {
        "control":   RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Triángulo" / "T1_triangulo_control.png",
        "invertido": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Triángulo" / "T1_triangulo_invertido.png",
        "triangulo": RUTA_BASE / "diseño_mascota" / "Tarea 1" / "Triángulo" / "T1_triangulo_triangulo.png",
    },
}

# =============================================================================
# ESTÍMULOS — TAREA 2
# Estructura: {variante: Path}
# =============================================================================
ESTIMULOS_T2 = {
    "baby":   RUTA_BASE / "diseño_mascota" / "Tarea 2" / "T2_baby.png",
    "bonito": RUTA_BASE / "diseño_mascota" / "Tarea 2" / "T2_bonito.png",
    "niño":   RUTA_BASE / "diseño_mascota" / "Tarea 2" / "T2_niño.png",
    "adulto": RUTA_BASE / "diseño_mascota" / "Tarea 2" / "T2_adulto.png",
}

# =============================================================================
# TIEMPOS (segundos) — experimento real
# =============================================================================
TIEMPOS = {
    "tarea1": {"fijacion_s": 1.0, "visualizacion_s": 10.0},
    "tarea2": {"fijacion_s": 1.0, "visualizacion_s": 10.0},
}

# TIEMPOS_SIMULACION — para dry-runs sin esperar en tiempo real
TIEMPOS_SIMULACION = {
    "tarea1": {"fijacion_s": 0.5, "visualizacion_s": 5.0},
    "tarea2": {"fijacion_s": 0.5, "visualizacion_s": 5.0},
}

REPETICIONES = 4

# =============================================================================
# EYE TRACKER (Tobii Pro Fusion)
# =============================================================================
TASA_MUESTREO_HZ   = 250
CALIBRACION_PUNTOS = 9

# =============================================================================
# PANTALLA
# =============================================================================
PANTALLA_RESOLUCION  = (1920, 1080)
PANTALLA_FULLSCREEN  = True
PANTALLA_COLOR_FONDO = [0.5, 0.5, 0.5]
DISTANCIA_CM         = 65
MONITOR_NOMBRE       = "monitor_lab"

# =============================================================================
# DISPOSICIÓN EN PANTALLA
# =============================================================================
TAMANO_IMG_PAR    = (500, 500)
POS_PAR           = {"izquierda": (-460, 0), "derecha": (460, 0)}

TAMANO_IMG_GRID   = (400, 400)
POS_GRID          = {
    "top_left":  (-460,  270),
    "top_right": ( 460,  270),
    "bot_left":  (-460, -270),
    "bot_right": ( 460, -270),
}

FIJACION_TAMANO_PX = 40
FIJACION_COLOR     = "black"

# =============================================================================
# TECLAS
# =============================================================================
TECLA_SALIR   = "escape"
TECLA_AVANZAR = "space"


# =============================================================================
# FUNCIONES
# =============================================================================

def preparar_directorios(participante_id: str) -> Path:
    """Crea datos/<participante_id>/ y devuelve la ruta. Falla si ya existe."""
    ruta = RUTA_DATOS / participante_id
    if ruta.exists():
        raise FileExistsError(f"Ya existen datos para {participante_id}. Usa otro ID.")
    ruta.mkdir(parents=True)
    return ruta


def verificar_estimulos() -> bool:
    """Verifica que todos los archivos de estímulo existan. Lanza FileNotFoundError si falta alguno."""
    todos = list(ESTIMULOS_T2.values())
    for grupo in ESTIMULOS_T1.values():
        todos.extend(grupo.values())
    for ruta in todos:
        if not ruta.exists():
            raise FileNotFoundError(f"Estímulo no encontrado: {ruta}")
    return True
