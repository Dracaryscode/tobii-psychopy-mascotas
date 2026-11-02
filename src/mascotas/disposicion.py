"""Geometría del lienzo y disposición en pantalla (F10 §4.3, §7.4, §7.5 y §9.3).

Coordenadas en píxeles de pantalla, origen en la esquina superior izquierda y
eje y hacia abajo (la convención de F10). Las funciones de presentación
convierten luego al sistema de PsychoPy.

Regla 2: se coloca siempre el lienzo completo en la misma posición; nunca se
centra la figura (la cola la hace asimétrica).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

YP_BASE_UC = 0.508          # posición de las pupilas de la base (PObas)
DX_PUPILAS_UC = 0.230       # distancia horizontal de cada pupila al eje de la figura


@dataclass(frozen=True)
class Lienzo:
    """Esquina superior izquierda y tamaño de un lienzo en la pantalla."""
    x: int
    y: int
    ancho: int
    alto: int

    @property
    def centro_x(self) -> float:
        return self.x + self.ancho / 2


def vertice(h_px: int) -> tuple[float, float]:
    """Vértice V en coordenadas del lienzo: (0,8·h_px; 0,2·h_px)."""
    return 0.8 * h_px, 0.2 * h_px


def pupilas_en_lienzo(h_px: int, yP_uc: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """Centros de las pupilas en el lienzo (Tabla 3)."""
    vx, vy = vertice(h_px)
    y = vy + yP_uc * h_px
    return (vx - DX_PUPILAS_UC * h_px, y), (vx + DX_PUPILAS_UC * h_px, y)


def lienzos_duelo(
    ancho_pantalla: int, ancho_lienzo: int, alto_lienzo: int,
    separacion_centros_px: int, borde_superior_px: int,
) -> tuple[Lienzo, Lienzo]:
    """Lienzos izquierdo y derecho, simétricos respecto del centro y a la misma altura."""
    cx = ancho_pantalla / 2
    izq = Lienzo(round(cx - separacion_centros_px - ancho_lienzo / 2), borde_superior_px, ancho_lienzo, alto_lienzo)
    der = Lienzo(round(cx + separacion_centros_px - ancho_lienzo / 2), borde_superior_px, ancho_lienzo, alto_lienzo)
    if izq.x < 0 or der.x + ancho_lienzo > ancho_pantalla:
        raise ValueError("Los lienzos del duelo no caben en el ancho de la pantalla")
    if izq.x + ancho_lienzo > der.x:
        raise ValueError("Los lienzos del duelo se superponen")
    return izq, der


def lienzo_valoracion(ancho_lienzo: int, alto_lienzo: int, centro_x_px: int, borde_superior_px: int) -> Lienzo:
    """Lienzo de las fases 2 a 4; la pregunta y la escala van a su derecha."""
    return Lienzo(round(centro_x_px - ancho_lienzo / 2), borde_superior_px, ancho_lienzo, alto_lienzo)


def posicion_cruz(
    ancho_pantalla: int, alto_pantalla: int, h_px: int, borde_superior_px: int, modo: str = "pupilas_base",
) -> tuple[float, float]:
    """Centro horizontal; altura de las pupilas de la base o centro vertical (F10 §7.4)."""
    if modo == "pupilas_base":
        _, y = pupilas_en_lienzo(h_px, YP_BASE_UC)[0]
        return ancho_pantalla / 2, borde_superior_px + y
    if modo == "centro_pantalla":
        return ancho_pantalla / 2, alto_pantalla / 2
    raise ValueError(f"Modo de cruz desconocido: {modo}")


def pixeles_por_grado(distancia_mm: float, tamano_pixel_mm: float) -> float:
    """px/° = distancia × tan(1°) / tamaño del píxel (F10 §5)."""
    return distancia_mm * math.tan(math.radians(1)) / tamano_pixel_mm
