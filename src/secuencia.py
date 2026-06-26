"""
secuencia.py — Generación de la secuencia de ensayos.

Lógica pura, sin PsychoPy ni Tobii: completamente testeable.
"""

import random
from itertools import combinations
from pathlib import Path

try:
    from . import config
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src import config


def _rng(participante_id: str) -> random.Random:
    return random.Random(hash(participante_id) % (2**32))


def _generar_tarea1(participante_id: str) -> list[dict]:
    rng = _rng(participante_id)
    ensayos: list[dict] = []

    for rep in range(1, config.REPETICIONES + 1):
        bloque = []
        for grupo, variantes in config.ESTIMULOS_T1.items():
            items = list(variantes.items())  # [(nombre_variante, Path), ...]
            for (va_key, va_path), (vb_key, vb_path) in combinations(items, 2):
                bloque.append((grupo, va_path, vb_path))

        rng.shuffle(bloque)

        for grupo, va_path, vb_path in bloque:
            # Contrabalanceo: reps impares → primer elemento a izquierda
            if rep % 2 == 1:
                izq_path, der_path = va_path, vb_path
            else:
                izq_path, der_path = vb_path, va_path

            ensayos.append({
                "ensayo":    0,
                "grupo":     grupo,
                "imagen_izq": izq_path,
                "imagen_der": der_path,
                "nombre_izq": izq_path.stem,
                "nombre_der": der_path.stem,
                "repeticion": rep,
            })

    for i, e in enumerate(ensayos, 1):
        e["ensayo"] = i

    return ensayos


def _generar_tarea2(participante_id: str) -> list[dict]:
    rng   = _rng(participante_id)
    items = list(config.ESTIMULOS_T2.items())  # [(variante, Path), ...]
    ensayos: list[dict] = []

    for rep in range(1, config.REPETICIONES + 1):
        bloque = list(combinations(items, 2))   # C(4,2) = 6 pares
        rng.shuffle(bloque)

        for (va_key, va_path), (vb_key, vb_path) in bloque:
            # Contrabalanceo: reps impares → primer elemento a izquierda
            if rep % 2 == 1:
                izq_path, der_path = va_path, vb_path
            else:
                izq_path, der_path = vb_path, va_path

            ensayos.append({
                "ensayo":     0,
                "imagen_izq": izq_path,
                "imagen_der": der_path,
                "nombre_izq": izq_path.stem,
                "nombre_der": der_path.stem,
                "repeticion": rep,
            })

    for i, e in enumerate(ensayos, 1):
        e["ensayo"] = i

    return ensayos


def generar_secuencia(participante_id: str) -> dict:
    """
    Devuelve {"tarea1": [...], "tarea2": [...]} con la secuencia completa
    del participante. Reproducible dado el mismo participante_id.
    """
    return {
        "tarea1": _generar_tarea1(participante_id),
        "tarea2": _generar_tarea2(participante_id),
    }


if __name__ == "__main__":
    import sys
    from collections import Counter

    pid = sys.argv[1] if len(sys.argv) > 1 else "TEST01"
    seq = generar_secuencia(pid)

    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  Secuencia para participante: {pid}")
    print(sep)

    t1 = seq["tarea1"]
    print(f"\nTAREA 1 — {len(t1)} ensayos  (esperado 36)")
    for e in t1:
        print(f"  [{e['ensayo']:02d}] rep={e['repeticion']}  "
              f"grupo={e['grupo']:<10}  "
              f"izq={e['nombre_izq']:<25}  der={e['nombre_der']}")

    t2 = seq["tarea2"]
    print(f"\nTAREA 2 — {len(t2)} ensayos  (esperado 24)")
    for e in t2:
        print(f"  [{e['ensayo']:02d}] rep={e['repeticion']}  "
              f"izq={e['nombre_izq']:<20}  der={e['nombre_der']}")

    # Verificaciones rápidas
    print(f"\n{sep}")
    print("  Verificación:")
    grupos = Counter(e["grupo"] for e in t1)
    print(f"  T1 ensayos por grupo: {dict(grupos)}  (esperado 12 c/u)")

    pares_t2 = Counter(
        tuple(sorted([e["nombre_izq"], e["nombre_der"]])) for e in t2
    )
    print(f"  T2 pares únicos: {len(pares_t2)}  (esperado 6)")
    for par, n in sorted(pares_t2.items()):
        print(f"    {par[0]} vs {par[1]}: {n} veces  (esperado {config.REPETICIONES})")
    print(sep)
