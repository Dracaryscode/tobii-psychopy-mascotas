"""Aleatorización y control del orden (documento maestro F10, §8).

- La semilla se genera al iniciar la sesión y se registra [D].
- Con la misma semilla y la misma versión del programa, los órdenes de las
  cuatro fases y los intervalos aleatorios se reproducen exactamente [P].
- Cada uso tiene su propio generador derivado de la semilla, así que añadir un
  sorteo en una fase no cambia los órdenes de las demás.

`random.Random` con una semilla de texto es determinista entre procesos (a
diferencia de `hash()`), por eso se usa aquí.
"""

from __future__ import annotations

import random
import secrets
from dataclasses import dataclass, field
from typing import Sequence

from .estimulos import Ensayo, codigos_esperados

MIXTA = "Mixta"


class ErrorAleatorizacion(Exception):
    """No se encontró un orden que cumpla las restricciones."""


def nueva_semilla() -> int:
    """Semilla aleatoria de la sesión (se guarda en sesion.json)."""
    return secrets.randbits(32)


def generador(semilla: int, uso: str) -> random.Random:
    """Generador independiente para cada uso (fase1, fase2, iti, ...)."""
    return random.Random(f"mascotas:{semilla}:{uso}")


def infracciones_fase1(orden: Sequence[Ensayo], max_racha: int = 3) -> list[str]:
    """Devuelve las infracciones de las restricciones de F10 §8.1 (vacía si cumple).

    1. El mismo par_id no aparece en dos ensayos consecutivos.
    2. No más de `max_racha` ensayos seguidos de la misma identidad; los
       rellenos («Mixta») interrumpen la racha.
    """
    problemas = []
    racha = 0
    anterior = None
    for n, e in enumerate(orden, start=1):
        if anterior is not None and e.par_id == anterior.par_id:
            problemas.append(f"Ensayos {n - 1} y {n}: mismo par {e.par_id}")
        if e.identidad == MIXTA:
            racha = 0
        elif anterior is not None and e.identidad == anterior.identidad:
            racha += 1
        else:
            racha = 1
        if racha > max_racha:
            problemas.append(f"Ensayo {n}: {racha} seguidos de {e.identidad}")
        anterior = e
    return problemas


@dataclass
class OrdenFase1:
    ensayos: list[Ensayo]
    intentos: int


def orden_fase1(
    ensayos: Sequence[Ensayo],
    rng: random.Random,
    max_racha: int = 3,
    max_intentos: int = 10000,
) -> OrdenFase1:
    """Muestreo con rechazo (F10 §8.1): baraja hasta cumplir las restricciones."""
    lista = list(ensayos)
    for intento in range(1, max_intentos + 1):
        rng.shuffle(lista)
        if not infracciones_fase1(lista, max_racha):
            return OrdenFase1(list(lista), intento)
    raise ErrorAleatorizacion(
        f"No se encontró un orden válido para la fase 1 en {max_intentos} intentos"
    )


def orden_valoraciones(rng: random.Random, codigos: Sequence[str] | None = None) -> list[str]:
    """Orden aleatorio de las 36 imágenes para una fase de valoración (F10 §8.2)."""
    lista = list(codigos) if codigos is not None else codigos_esperados()
    rng.shuffle(lista)
    return lista


def intervalos_ms(rng: random.Random, n: int, minimo: int, maximo: int) -> list[int]:
    """Intervalos entre duelos con distribución uniforme (F10 §7.4, paso 4)."""
    return [rng.randint(minimo, maximo) for _ in range(n)]


@dataclass
class OrdenesSesion:
    semilla: int
    fase1: list[Ensayo]
    intentos_fase1: int
    iti_fase1_ms: list[int]
    fase2: list[str]
    fase3: list[str]
    fase4: list[str]
    orden_preguntas_fase3: list[str] = field(default_factory=lambda: ["agrado", "edad"])

    def como_dict(self) -> dict:
        """Listas explícitas para los metadatos de la sesión (F10 §8.3)."""
        return {
            "semilla": self.semilla,
            "fase1": [e.ensayo_id for e in self.fase1],
            "intentos_fase1": self.intentos_fase1,
            "iti_fase1_ms": self.iti_fase1_ms,
            "fase2": self.fase2,
            "fase3": self.fase3,
            "fase4": self.fase4,
            "orden_preguntas_fase3": self.orden_preguntas_fase3,
        }


def generar_ordenes(
    semilla: int,
    ensayos_fase1: Sequence[Ensayo],
    iti_min_ms: int = 500,
    iti_max_ms: int = 1000,
    max_racha: int = 3,
    max_intentos: int = 10000,
    contrabalancear_agrado_edad: bool = False,
    numero_participante: int | None = None,
) -> OrdenesSesion:
    """Todos los órdenes de una sesión a partir de su semilla."""
    f1 = orden_fase1(ensayos_fase1, generador(semilla, "fase1"), max_racha, max_intentos)
    preguntas = ["agrado", "edad"]
    if contrabalancear_agrado_edad and numero_participante is not None and numero_participante % 2 == 0:
        preguntas = ["edad", "agrado"]
    return OrdenesSesion(
        semilla=semilla,
        fase1=f1.ensayos,
        intentos_fase1=f1.intentos,
        iti_fase1_ms=intervalos_ms(generador(semilla, "iti_fase1"), len(f1.ensayos), iti_min_ms, iti_max_ms),
        fase2=orden_valoraciones(generador(semilla, "fase2")),
        fase3=orden_valoraciones(generador(semilla, "fase3")),
        fase4=orden_valoraciones(generador(semilla, "fase4")),
        orden_preguntas_fase3=preguntas,
    )
