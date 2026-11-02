"""Preparación de una sesión: todo lo que se comprueba antes de mostrar nada.

1. Carga y valida la configuración.
2. Verifica los 36 estímulos contra el manifiesto (prueba de aceptación 1).
3. Lee y valida la lista de duelos (prueba 4).
4. Genera la semilla y todos los órdenes.

No necesita PsychoPy ni el eye tracker.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import aleatorizacion, estimulos
from .config import Configuracion


@dataclass
class Preparacion:
    estimulos: dict[str, estimulos.Estimulo]
    ensayos_fase1: list[estimulos.Ensayo]
    ordenes: aleatorizacion.OrdenesSesion


def verificar_practica(cfg: Configuracion) -> list[Path]:
    """Comprueba que existen las imágenes de práctica y que ninguna es experimental (regla 4)."""
    carpeta = cfg.ruta(cfg["estimulos"]["carpeta_practica"])
    rutas = []
    faltan = []
    for nombre in cfg["practica"]["imagenes"]:
        if estimulos.PATRON_ARCHIVO.match(nombre):
            raise estimulos.ErrorEstimulos(f"La práctica no puede usar imágenes experimentales: {nombre}")
        ruta = carpeta / nombre
        (rutas if ruta.exists() else faltan).append(ruta)
    if faltan:
        raise estimulos.ErrorEstimulos(
            "Faltan imágenes de práctica:\n- " + "\n- ".join(str(r) for r in faltan)
        )
    return rutas


def preparar(cfg: Configuracion, semilla: int | None = None, verificar_archivos: bool = True) -> Preparacion:
    e = cfg["estimulos"]
    ruta_manifiesto = cfg.ruta(e["manifiesto"])
    if verificar_archivos or ruta_manifiesto.exists():
        manifiesto = estimulos.leer_manifiesto(ruta_manifiesto)
    else:
        manifiesto = {}
    if verificar_archivos:
        estimulos.verificar(
            cfg.ruta(e["carpeta_experimentales"]), manifiesto,
            e["lienzo_ancho_px"], e["lienzo_alto_px"], e["verificar_sha256"],
        )
        verificar_practica(cfg)
    ensayos = estimulos.leer_ensayos_fase1(cfg.ruta(e["ensayos_fase1"]))
    estimulos.verificar_composicion_fase1(ensayos)

    d = cfg["duelos"]
    ordenes = aleatorizacion.generar_ordenes(
        semilla if semilla is not None else aleatorizacion.nueva_semilla(),
        ensayos,
        iti_min_ms=d["iti_min_ms"], iti_max_ms=d["iti_max_ms"],
        max_racha=d["max_racha_misma_identidad"], max_intentos=d["max_intentos_aleatorizacion"],
        contrabalancear_agrado_edad=cfg["valoraciones"]["contrabalancear_agrado_edad"],
    )
    return Preparacion(manifiesto, ensayos, ordenes)
