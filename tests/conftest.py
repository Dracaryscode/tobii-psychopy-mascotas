import csv
import hashlib
import struct
import sys
import zlib
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from mascotas import config, estimulos  # noqa: E402


def png_blanco(ruta: Path, ancho: int, alto: int, semilla: int = 0) -> None:
    """PNG mínimo en escala de grises (sin PIL). `semilla` cambia un píxel para variar la huella."""
    fila = b"\x00" + bytes([255] * ancho)
    filas = [fila] * alto
    filas[0] = b"\x00" + bytes([semilla % 256]) + bytes([255] * (ancho - 1))
    datos = zlib.compress(b"".join(filas))

    def bloque(tipo, contenido):
        return (struct.pack(">I", len(contenido)) + tipo + contenido
                + struct.pack(">I", zlib.crc32(tipo + contenido) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, 0, 0, 0, 0)
    ruta.write_bytes(b"\x89PNG\r\n\x1a\n" + bloque(b"IHDR", ihdr) + bloque(b"IDAT", datos) + bloque(b"IEND", b""))


@pytest.fixture(scope="session")
def cfg():
    return config.cargar()


@pytest.fixture(scope="session")
def ensayos(cfg):
    return estimulos.leer_ensayos_fase1(cfg.ruta(cfg["estimulos"]["ensayos_fase1"]))


@pytest.fixture
def carpeta_estimulos(tmp_path):
    """36 PNG de prueba de 592 × 1073 y su manifiesto, como los entregará la investigadora."""
    carpeta = tmp_path / "experimentales"
    carpeta.mkdir()
    yp = {"sub": 0.478, "bas": 0.508, "baj": 0.538}
    filas = []
    for i, codigo in enumerate(estimulos.codigos_esperados()):
        n = estimulos.niveles(codigo)
        archivo = f"MCv2_{codigo.replace('-', '_')}_v5.png"
        png_blanco(carpeta / archivo, 592, 1073, semilla=i)
        filas.append({
            "codigo": codigo, "archivo": archivo, "identidad": n["identidad"],
            "OJ": n["OJ"], "PO": n["PO"], "CU": n["CU"], "s": "1", "yP_uc": yp[n["PO"][2:]],
            "R": "1.862", "ancho_px": 592, "alto_px": 1073, "h_px": 370,
            "sha256": hashlib.sha256((carpeta / archivo).read_bytes()).hexdigest(),
        })
    with (carpeta / "estimulos_manifiesto.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=estimulos.COLUMNAS_MANIFIESTO)
        w.writeheader()
        w.writerows(filas)
    return carpeta
