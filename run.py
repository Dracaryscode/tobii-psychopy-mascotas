"""Punto de entrada de la tarea.

Por ahora solo está la preparación (verificar estímulos y generar órdenes).
Las fases con PsychoPy y el eye tracker llegan en los siguientes pasos del plan.

Ejemplos:
    python run.py verificar
    python run.py ordenes --semilla 20261102
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mascotas import config, preparacion  # noqa: E402
from mascotas.estimulos import ErrorEstimulos  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Mascotas científicas: tarea experimental (F10)")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("verificar", help="Comprueba configuración, estímulos y lista de duelos")
    o = sub.add_parser("ordenes", help="Genera y muestra los órdenes de una sesión")
    o.add_argument("--semilla", type=int, default=None)
    o.add_argument("--sin-archivos", action="store_true",
                   help="No verifica los PNG (útil antes de copiar las imágenes)")
    args = p.parse_args(argv)

    cfg = config.cargar()
    try:
        if args.comando == "verificar":
            prep = preparacion.preparar(cfg)
            print(f"OK: {len(prep.estimulos)} estímulos verificados, "
                  f"{len(prep.ensayos_fase1)} duelos, práctica presente.")
        else:
            prep = preparacion.preparar(cfg, args.semilla, verificar_archivos=not args.sin_archivos)
            print(json.dumps(prep.ordenes.como_dict(), ensure_ascii=False, indent=2))
    except ErrorEstimulos as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
