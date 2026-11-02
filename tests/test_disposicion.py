import pytest

from mascotas import disposicion as dp


def test_duelo_como_figura_3_de_f10():
    """Con 1920 × 1080: centros en x = 480 y 1440, borde superior y = 3, vértices en y = 77."""
    izq, der = dp.lienzos_duelo(1920, 592, 1073, 480, 3)
    assert izq.centro_x == 480 and der.centro_x == 1440
    assert izq.y == der.y == 3
    assert izq.y + dp.vertice(370)[1] == 77


def test_cruz_a_la_altura_de_las_pupilas_base():
    x, y = dp.posicion_cruz(1920, 1080, 370, 3)
    assert x == 960
    assert y == pytest.approx(265, abs=0.5)


def test_pupilas_tabla_3():
    (xi, y_sub), (xd, _) = dp.pupilas_en_lienzo(370, 0.478)
    assert xi == pytest.approx(210.9, abs=0.1) and xd == pytest.approx(381.1, abs=0.1)
    assert y_sub == pytest.approx(250.9, abs=0.1)
    assert dp.pupilas_en_lienzo(370, 0.538)[0][1] == pytest.approx(273.1, abs=0.1)


def test_lienzo_valoracion():
    lz = dp.lienzo_valoracion(592, 1073, 640, 3)
    assert (lz.x, lz.y, lz.centro_x) == (344, 3, 640)


def test_pixeles_por_grado():
    assert dp.pixeles_por_grado(600, 0.275) == pytest.approx(38, abs=0.5)


def test_lienzos_que_no_caben():
    with pytest.raises(ValueError):
        dp.lienzos_duelo(1280, 592, 1073, 480, 3)
