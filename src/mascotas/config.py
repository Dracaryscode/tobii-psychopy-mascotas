"""Carga y validación de la configuración (config/*.yaml).

Todos los parámetros [P] y [X] del documento maestro F10 (Tabla 9) viven en
config/parametros.yaml y los textos para el participante en config/textos.yaml.
El código nunca fija esos valores.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_CONFIG = RAIZ / "config"

SECCIONES_PARAMETROS = (
    "pantalla", "estimulos", "practica", "calibracion", "duelos",
    "valoraciones", "pausas", "aoi", "calidad", "datos",
)
ITEMS_OBLIGATORIOS = ("eleccion", "ternura", "agrado", "edad", "extraneza", "abierta_cierre")


class ErrorConfiguracion(Exception):
    """La configuración falta o está incompleta."""


@dataclass(frozen=True)
class Configuracion:
    parametros: dict[str, Any]
    textos: dict[str, Any]
    cierre: dict[str, Any]
    raiz: Path

    def ruta(self, relativa: str) -> Path:
        """Resuelve una ruta de la configuración respecto a la raíz del proyecto."""
        p = Path(relativa)
        return p if p.is_absolute() else self.raiz / p

    def __getitem__(self, seccion: str) -> dict[str, Any]:
        return self.parametros[seccion]


def _leer_yaml(ruta: Path) -> dict[str, Any]:
    if not ruta.exists():
        raise ErrorConfiguracion(f"No existe el archivo de configuración: {ruta}")
    with ruta.open(encoding="utf-8") as f:
        datos = yaml.safe_load(f)
    if not isinstance(datos, dict):
        raise ErrorConfiguracion(f"El archivo {ruta} está vacío o mal formado")
    return datos


def validar(parametros: dict[str, Any], textos: dict[str, Any]) -> None:
    faltan = [s for s in SECCIONES_PARAMETROS if s not in parametros]
    if faltan:
        raise ErrorConfiguracion(f"Faltan secciones en parametros.yaml: {', '.join(faltan)}")

    items = textos.get("items", {})
    faltan = [i for i in ITEMS_OBLIGATORIOS if not items.get(i, {}).get("pregunta")]
    if faltan:
        raise ErrorConfiguracion(f"Faltan ítems en textos.yaml: {', '.join(faltan)}")

    cal = parametros["calibracion"]
    if not 5 <= cal["puntos"] <= 9:
        raise ErrorConfiguracion("calibracion.puntos debe estar entre 5 y 9 [D]")

    d = parametros["duelos"]
    if d["iti_min_ms"] > d["iti_max_ms"]:
        raise ErrorConfiguracion("duelos.iti_min_ms no puede ser mayor que iti_max_ms")
    if d["ventana_observacion_ms"] <= 0:
        raise ErrorConfiguracion("duelos.ventana_observacion_ms debe ser positiva")

    v = parametros["valoraciones"]
    if (v["escala_min"], v["escala_max"]) != (1, 7):
        raise ErrorConfiguracion("La escala de las valoraciones es de 1 a 7 [D]")

    e = parametros["estimulos"]
    h = e["h_px"]
    esperado = (round(1.6 * h), round(2.9 * h))
    if (e["lienzo_ancho_px"], e["lienzo_alto_px"]) != esperado:
        raise ErrorConfiguracion(
            f"El lienzo debe medir 1,6·h_px × 2,9·h_px = {esperado[0]} × {esperado[1]} px "
            f"con h_px = {h} (F10, Tabla 3)"
        )

    p = parametros["pantalla"]
    if e["lienzo_alto_px"] + d["borde_superior_px"] > p["alto_px"]:
        raise ErrorConfiguracion(
            "El lienzo no cabe en la altura de la pantalla. Las imágenes no se reescalan "
            "en el programa (regla 1): hay que regenerarlas con un h_px menor."
        )


def cargar(carpeta: Path | None = None, raiz: Path | None = None) -> Configuracion:
    carpeta = Path(carpeta) if carpeta else CARPETA_CONFIG
    parametros = _leer_yaml(carpeta / "parametros.yaml")
    textos = _leer_yaml(carpeta / "textos.yaml")
    cierre = _leer_yaml(carpeta / "cierre.yaml")
    validar(parametros, textos)
    return Configuracion(parametros, textos, cierre, Path(raiz) if raiz else RAIZ)
