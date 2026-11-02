import os
import subprocess
import sys
from collections import Counter

import pytest

from mascotas import aleatorizacion as al
from mascotas.estimulos import codigos_esperados


def test_prueba_5_diez_mil_ordenes_sin_infracciones(ensayos):
    """Prueba de aceptación 5 (F10 §11.2): 10 000 órdenes sin infracciones de §8.1."""
    intentos = []
    for semilla in range(10_000):
        o = al.orden_fase1(ensayos, al.generador(semilla, "fase1"))
        assert al.infracciones_fase1(o.ensayos) == []
        assert sorted(e.ensayo_id for e in o.ensayos) == sorted(e.ensayo_id for e in ensayos)
        intentos.append(o.intentos)
    # Con ~10 % de aceptación, la media debería rondar 10 intentos.
    assert 5 < sum(intentos) / len(intentos) < 20


def test_detecta_mismo_par_consecutivo(ensayos):
    por_id = {e.ensayo_id: e for e in ensayos}
    orden = [por_id["C01a"], por_id["C01b"]]
    assert any("mismo par" in p for p in al.infracciones_fase1(orden))


def test_detecta_racha_larga_y_relleno_la_corta(ensayos):
    por_id = {e.ensayo_id: e for e in ensayos}
    cuatro = [por_id[i] for i in ("C01a", "C04a", "C07a", "I01a")]
    assert any("seguidos" in p for p in al.infracciones_fase1(cuatro))
    con_relleno = [por_id[i] for i in ("C01a", "C04a", "C07a", "R01a", "C02a", "C05a", "C06a")]
    assert al.infracciones_fase1(con_relleno) == []


def test_ejemplo_del_excel_f12_cumple(ensayos):
    """Orden de ejemplo de la hoja Ejemplo_orden_fase1 (semilla 20261102 del Excel)."""
    ejemplo = ("I01b C04b I01a C14b C12b C11b C07a C13b C07b C09a C06a R02a C12a C04a C05a C01b "
               "C10b C14a C03b I02b C03a C13a R01b C11a C08a R02b C08b I02a C10a C02b C06b C09b "
               "C05b R01a C02a C01a").split()
    por_id = {e.ensayo_id: e for e in ensayos}
    assert al.infracciones_fase1([por_id[i] for i in ejemplo]) == []


# Prueba de aceptación 6 (parte de orden): cada imagen una vez por fase

def test_fases_2_a_4(ensayos):
    o = al.generar_ordenes(123, ensayos)
    for fase in (o.fase2, o.fase3, o.fase4):
        assert Counter(fase) == Counter(codigos_esperados())
    assert o.fase2 != o.fase3 != o.fase4   # órdenes independientes
    assert o.orden_preguntas_fase3 == ["agrado", "edad"]


def test_intervalos_en_rango(ensayos):
    o = al.generar_ordenes(7, ensayos, iti_min_ms=500, iti_max_ms=1000)
    assert len(o.iti_fase1_ms) == 36
    assert all(500 <= x <= 1000 for x in o.iti_fase1_ms)


def test_misma_semilla_mismo_orden(ensayos):
    a = al.generar_ordenes(20261102, ensayos).como_dict()
    b = al.generar_ordenes(20261102, ensayos).como_dict()
    c = al.generar_ordenes(20261103, ensayos).como_dict()
    assert a == b
    assert a["fase1"] != c["fase1"]


def test_reproducible_entre_procesos(cfg):
    """El error del código viejo: hash() cambiaba entre procesos. Aquí no debe pasar."""
    codigo = (
        "import sys; sys.path.insert(0, 'src');"
        "from mascotas import aleatorizacion as al, estimulos as es;"
        "e = es.leer_ensayos_fase1('diseno/ensayos_fase1.csv');"
        "print(al.generar_ordenes(42, e).como_dict())"
    )
    salidas = {
        subprocess.run([sys.executable, "-c", codigo], cwd=cfg.raiz, capture_output=True,
                       text=True, check=True, env={**os.environ, "PYTHONHASHSEED": str(s)}).stdout
        for s in (1, 2, 3)
    }
    assert len(salidas) == 1


def test_sin_orden_posible_avisa(ensayos):
    with pytest.raises(al.ErrorAleatorizacion):
        al.orden_fase1(ensayos, al.generador(1, "fase1"), max_racha=0, max_intentos=50)
