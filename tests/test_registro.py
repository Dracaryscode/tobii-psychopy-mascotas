import csv
import json
from datetime import datetime

import pytest

from mascotas import registro


@pytest.fixture
def sesion(tmp_path):
    s = registro.Sesion(tmp_path, "P001", 1, "automatico", "0.1.0-dev", inicio=datetime(2026, 11, 5, 10, 30))
    yield s
    s.cerrar()


def test_carpeta_y_archivos(sesion, tmp_path):
    assert sesion.carpeta == tmp_path / "P001_S1_20261105_1030"
    for nombre in ("sesion.json", "respuestas.csv", "eventos.csv", "registro.txt"):
        assert sesion.ruta(nombre).exists()


def test_columnas_del_anexo_c(sesion):
    with sesion.ruta("respuestas.csv").open(encoding="utf-8") as f:
        assert tuple(next(csv.reader(f))) == registro.COLUMNAS_RESPUESTAS


def test_respuesta_se_escribe_al_momento_y_numera(sesion):
    sesion.respuesta("1", ensayo_id="C01a", escala="eleccion", respuesta="izq")
    sesion.respuesta("1", ensayo_id="C02b", escala="eleccion", respuesta="der")
    sesion.respuesta("2", ensayo_id="ID1-OJmae-PObas-CUbas", escala="ternura", respuesta=5)
    # Se lee sin cerrar: los datos ya están en disco (regla 10).
    with sesion.ruta("respuestas.csv").open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert [(r["n_global"], r["n_fase"], r["fase"]) for r in filas] == [("1", "1", "1"), ("2", "2", "1"), ("3", "1", "2")]
    assert filas[0]["participante"] == "P001" and filas[0]["modo"] == "automatico"


def test_columna_fuera_del_anexo_c(sesion):
    with pytest.raises(registro.ErrorRegistro):
        sesion.respuesta("1", columna_inventada=1)


def test_interrupcion_queda_registrada(sesion):
    sesion.respuesta("1", ensayo_id="C01a")
    sesion.interrupcion("cierre forzado")
    meta = json.loads(sesion.ruta("sesion.json").read_text(encoding="utf-8"))
    assert meta["interrupciones"][0]["motivo"] == "cierre forzado"
    assert "INTERRUPCION" in sesion.ruta("registro.txt").read_text(encoding="utf-8")


def test_codigo_de_participante_invalido(tmp_path):
    with pytest.raises(registro.ErrorRegistro):
        registro.Sesion(tmp_path, "juan", 1, "real", "x")


def test_no_sobrescribe_una_sesion(tmp_path):
    inicio = datetime(2026, 11, 5, 10, 30)
    s = registro.Sesion(tmp_path, "P002", 1, "prueba", "x", inicio=inicio)
    s.cerrar()
    with pytest.raises(registro.ErrorRegistro):
        registro.Sesion(tmp_path, "P002", 1, "prueba", "x", inicio=inicio)
