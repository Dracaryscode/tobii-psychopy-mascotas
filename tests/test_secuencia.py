"""
test_secuencia.py — Pruebas de la generación de secuencia (sin hardware).

Uso:
    python -m pytest tests/ -v
"""

import sys
from pathlib import Path
from collections import Counter
from itertools import combinations

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, secuencia


# ---------------------------------------------------------------------------
# Totales correctos
# ---------------------------------------------------------------------------

def test_total_tarea1():
    # 3 grupos × C(3,2)=3 pares × 4 repeticiones = 36
    ens = secuencia.tarea1("P01")
    esperado = 3 * 3 * config.REPETICIONES
    assert len(ens) == esperado, f"esperado {esperado}, obtenido {len(ens)}"


def test_total_tarea2():
    # 4 estímulos × 4 repeticiones = 16
    ens = secuencia.tarea2("P01")
    esperado = len(config.ESTIMULOS_T2) * config.REPETICIONES
    assert len(ens) == esperado, f"esperado {esperado}, obtenido {len(ens)}"


# ---------------------------------------------------------------------------
# Estructura de cada ensayo
# ---------------------------------------------------------------------------

def test_campos_requeridos():
    for fn in (secuencia.tarea1, secuencia.tarea2):
        for e in fn("P01"):
            for campo in ("tarea", "n_ensayo", "repeticion", "grupo",
                          "variante", "aoi", "estimulos"):
                assert campo in e, f"Campo '{campo}' ausente"


def test_tarea1_dos_estimulos_lados():
    for e in secuencia.tarea1("P01"):
        assert len(e["estimulos"]) == 2
        posiciones = {s["posicion"] for s in e["estimulos"]}
        assert posiciones == {"izquierda", "derecha"}


def test_tarea2_un_estimulo_centro():
    for e in secuencia.tarea2("P01"):
        assert len(e["estimulos"]) == 1
        assert e["estimulos"][0]["posicion"] == "centro"


def test_archivos_en_disco():
    faltantes = []
    vistos = set()
    for fn in (secuencia.tarea1, secuencia.tarea2):
        for e in fn("P01"):
            for est in e["estimulos"]:
                ruta = config.ESTIMULOS_DIR / est["archivo"]
                if not ruta.exists() and est["archivo"] not in vistos:
                    faltantes.append(est["archivo"])
                    vistos.add(est["archivo"])
    assert not faltantes, "Imágenes faltantes:\n" + "\n".join(faltantes)


# ---------------------------------------------------------------------------
# Balance: cada PAR de estímulos aparece exactamente REPETICIONES veces
# ---------------------------------------------------------------------------

def test_tarea1_todos_los_pares_presentes():
    ensayos = secuencia.tarea1("P01")
    for grupo, variantes in config.GRUPOS_T1.items():
        nombres = [v["nombre"] for v in variantes]
        pares_esperados = set(
            tuple(sorted(p)) for p in combinations(nombres, 2)
        )
        pares_vistos = Counter()
        for e in ensayos:
            if e["grupo"] == grupo:
                par = tuple(sorted(s["nombre"] for s in e["estimulos"]))
                pares_vistos[par] += 1

        assert set(pares_vistos.keys()) == pares_esperados, \
            f"Grupo '{grupo}': pares incorrectos"
        for par, n in pares_vistos.items():
            assert n == config.REPETICIONES, \
                f"Grupo '{grupo}' par {par}: {n} veces (esperado {config.REPETICIONES})"


def test_tarea2_balance():
    conteo = Counter(e["variante"] for e in secuencia.tarea2("P01"))
    for variante, n in conteo.items():
        assert n == config.REPETICIONES, \
            f"Variante '{variante}': {n} veces (esperado {config.REPETICIONES})"


# ---------------------------------------------------------------------------
# Contrabalanceo izquierda/derecha en Tarea 1
# ---------------------------------------------------------------------------

def test_tarea1_contrabalanceo():
    ensayos = secuencia.tarea1("P01")
    izq = Counter()
    der = Counter()
    for e in ensayos:
        for s in e["estimulos"]:
            (izq if s["posicion"] == "izquierda" else der)[s["nombre"]] += 1
    # Cada estímulo participa en 2 pares × 4 reps = 8 apariciones.
    # El reparto izquierda/derecha debe estar equilibrado (diferencia ≤ 2).
    todos = set(izq) | set(der)
    for nombre in todos:
        assert abs(izq[nombre] - der[nombre]) <= 2, \
            f"'{nombre}': izq={izq[nombre]}, der={der[nombre]} — desequilibrado"


# ---------------------------------------------------------------------------
# Pseudoaleatorizacion en bloques (Tarea 1)
# Dentro de cada repetición, los 3 pares de un mismo grupo deben aparecer juntos.
# ---------------------------------------------------------------------------

def test_tarea1_pseudoaleatorizacion_bloques():
    ensayos = secuencia.tarea1("P01")
    reps = {}
    for e in ensayos:
        reps.setdefault(e["repeticion"], []).append(e["grupo"])

    for rep, seq in reps.items():
        i = 0
        while i < len(seq):
            grupo_actual = seq[i]
            bloque = seq[i:i+3]
            assert all(g == grupo_actual for g in bloque), \
                f"Rep {rep}: grupo '{grupo_actual}' no forma bloque. Seq: {seq}"
            i += 3


# ---------------------------------------------------------------------------
# AOI correctamente asignado
# ---------------------------------------------------------------------------

def test_tarea1_aoi():
    for e in secuencia.tarea1("P01"):
        if e["grupo"] == "Ojos":
            assert e["aoi"] == "Ojos"
        elif e["grupo"] in ("Cabeza", "Triangulo"):
            assert e["aoi"] == "Cabeza"


def test_tarea2_aoi():
    for e in secuencia.tarea2("P01"):
        assert e["aoi"] == "Ojos|Cabeza|Cuerpo"


# ---------------------------------------------------------------------------
# Reproducibilidad y semillas distintas por participante
# ---------------------------------------------------------------------------

def test_reproducibilidad():
    for fn in (secuencia.tarea1, secuencia.tarea2):
        a = [e["variante"] for e in fn("P07")]
        b = [e["variante"] for e in fn("P07")]
        assert a == b


def test_semillas_distintas():
    a = [e["variante"] for e in secuencia.tarea1("P01")]
    b = [e["variante"] for e in secuencia.tarea1("P99")]
    assert a != b


# ---------------------------------------------------------------------------
# Numeración consecutiva
# ---------------------------------------------------------------------------

def test_numeracion():
    for fn in (secuencia.tarea1, secuencia.tarea2):
        ens = fn("P01")
        assert [e["n_ensayo"] for e in ens] == list(range(1, len(ens) + 1))
