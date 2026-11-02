import pytest

from mascotas import estimulos
from mascotas.estimulos import ErrorEstimulos


def test_codigo_desde_archivo():
    assert estimulos.codigo_desde_archivo("MCv2_ID1_OJmae_PObas_CUbas_v5.png") == "ID1-OJmae-PObas-CUbas"
    with pytest.raises(ErrorEstimulos):
        estimulos.codigo_desde_archivo("T1_ojos_grandes.png")


def test_36_condiciones():
    codigos = estimulos.codigos_esperados()
    assert len(codigos) == len(set(codigos)) == 36
    assert codigos[0] == "ID1-OJpeq-POsub-CUbas"   # mismo orden que la hoja Estimulos_36


# Prueba de aceptación 1: integridad de los estímulos

def test_verificacion_correcta(carpeta_estimulos):
    m = estimulos.leer_manifiesto(carpeta_estimulos / "estimulos_manifiesto.csv")
    estimulos.verificar(carpeta_estimulos, m, 592, 1073)


def test_falta_un_archivo(carpeta_estimulos):
    m = estimulos.leer_manifiesto(carpeta_estimulos / "estimulos_manifiesto.csv")
    (carpeta_estimulos / "MCv2_ID2_OJgra_PObaj_CUlar_v5.png").unlink()
    with pytest.raises(ErrorEstimulos, match="Falta el archivo"):
        estimulos.verificar(carpeta_estimulos, m, 592, 1073)


def test_huella_distinta(carpeta_estimulos):
    m = estimulos.leer_manifiesto(carpeta_estimulos / "estimulos_manifiesto.csv")
    from conftest import png_blanco
    png_blanco(carpeta_estimulos / "MCv2_ID1_OJmae_PObas_CUbas_v5.png", 592, 1073, semilla=200)
    with pytest.raises(ErrorEstimulos, match="SHA-256"):
        estimulos.verificar(carpeta_estimulos, m, 592, 1073)


def test_tamano_distinto(carpeta_estimulos):
    m = estimulos.leer_manifiesto(carpeta_estimulos / "estimulos_manifiesto.csv")
    with pytest.raises(ErrorEstimulos, match="se esperaba"):
        estimulos.verificar(carpeta_estimulos, m, 600, 1073, comprobar_sha256=False)


# Prueba de aceptación 4: composición de la fase 1

def test_composicion_fase1(ensayos):
    estimulos.verificar_composicion_fase1(ensayos)


def test_composicion_detecta_par_sin_inversion(ensayos):
    malos = list(ensayos)
    c01b = next(i for i, e in enumerate(malos) if e.ensayo_id == "C01b")
    e = malos[c01b]
    malos[c01b] = estimulos.Ensayo(e.ensayo_id, e.tipo, e.par_id, e.identidad, e.rasgo, e.img_der, e.img_izq)
    with pytest.raises(ErrorEstimulos, match="C01"):
        estimulos.verificar_composicion_fase1(malos)


def test_csv_coincide_con_documento_f10(cfg, ensayos):
    """diseno/ensayos_fase1.csv es copia exacta del CSV de F10 guardado en docs/."""
    original = cfg.ruta("docs/diseno/F10_ensayos_fase1_definicion_v1.csv").read_bytes()
    assert cfg.ruta("diseno/ensayos_fase1.csv").read_bytes() == original
