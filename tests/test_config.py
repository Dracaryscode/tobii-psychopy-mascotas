import copy

import pytest

from mascotas import config


def test_carga_configuracion_por_defecto(cfg):
    assert cfg["pantalla"]["color_fondo"] == "#FFFFFF"
    assert cfg["duelos"]["ventana_observacion_ms"] == 5000
    assert cfg["estimulos"]["h_px"] == 370


def test_textos_literales_de_f10(cfg):
    """Prueba de aceptación 7 (parcial): enunciados [D] tal como en F10 §7."""
    items = cfg.textos["items"]
    assert items["eleccion"]["pregunta"] == "¿Cuál te parece más tierno?"
    assert items["ternura"]["pregunta"] == "¿Qué tan tierno te parece este personaje?"
    assert items["agrado"]["pregunta"] == "¿Cuánto te gusta este personaje?"
    assert items["extraneza"]["pregunta"] == "¿Qué tan raro o inquietante te parece este personaje?"
    assert items["edad"]["ancla_min"] == "Cría" and items["edad"]["ancla_max"] == "Adulto"
    assert items["abierta_cierre"]["pregunta"] == (
        "¿Notaste algo especial en los personajes? ¿En qué se diferenciaban?"
    )


def test_ningun_texto_menciona_rasgos(cfg):
    """F10 §7.4 y Anexo D: las instrucciones no mencionan ojos, cuerpo ni diferencias."""
    for clave, texto in cfg.textos["instrucciones"].items():
        t = texto.lower()
        for palabra in ("ojo", "cuerpo", "diferenc"):
            assert palabra not in t, f"La instrucción '{clave}' menciona '{palabra}'"


def test_lienzo_que_no_cabe_se_rechaza(cfg):
    p = copy.deepcopy(cfg.parametros)
    p["pantalla"]["alto_px"] = 1050
    with pytest.raises(config.ErrorConfiguracion, match="no se reescalan"):
        config.validar(p, cfg.textos)


def test_lienzo_incoherente_con_h_px(cfg):
    p = copy.deepcopy(cfg.parametros)
    p["estimulos"]["h_px"] = 300
    with pytest.raises(config.ErrorConfiguracion, match="1,6"):
        config.validar(p, cfg.textos)


def test_escala_distinta_de_1_a_7(cfg):
    p = copy.deepcopy(cfg.parametros)
    p["valoraciones"]["escala_max"] = 5
    with pytest.raises(config.ErrorConfiguracion):
        config.validar(p, cfg.textos)
