import copy
import dataclasses

import pytest

from conftest import png_blanco
from mascotas import preparacion
from mascotas.estimulos import ErrorEstimulos


@pytest.fixture
def cfg_temporal(cfg, carpeta_estimulos):
    """Configuración real, pero con los estímulos de prueba en una carpeta temporal."""
    p = copy.deepcopy(cfg.parametros)
    p["estimulos"]["carpeta_experimentales"] = str(carpeta_estimulos)
    p["estimulos"]["manifiesto"] = str(carpeta_estimulos / "estimulos_manifiesto.csv")
    practica = carpeta_estimulos.parent / "practica"
    practica.mkdir()
    for nombre in p["practica"]["imagenes"]:
        png_blanco(practica / nombre, 592, 1073)
    p["estimulos"]["carpeta_practica"] = str(practica)
    return dataclasses.replace(cfg, parametros=p)


def test_preparacion_completa(cfg_temporal):
    prep = preparacion.preparar(cfg_temporal, semilla=99)
    assert len(prep.estimulos) == 36
    assert len(prep.ordenes.fase1) == 36
    assert prep.ordenes.semilla == 99


def test_falta_practica(cfg_temporal):
    (cfg_temporal.ruta(cfg_temporal["estimulos"]["carpeta_practica"]) / "MCpractica_conejo_lisa_v5.png").unlink()
    with pytest.raises(ErrorEstimulos, match="práctica"):
        preparacion.preparar(cfg_temporal)


def test_practica_no_puede_usar_imagenes_experimentales(cfg_temporal):
    p = copy.deepcopy(cfg_temporal.parametros)
    p["practica"]["imagenes"] = ["MCv2_ID1_OJmae_PObas_CUbas_v5.png"]
    with pytest.raises(ErrorEstimulos, match="experimentales"):
        preparacion.preparar(dataclasses.replace(cfg_temporal, parametros=p))
