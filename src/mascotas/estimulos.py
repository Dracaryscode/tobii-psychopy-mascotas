"""Estímulos: códigos de condición, manifiesto, verificación y lista de duelos.

El programa no genera ni modifica imágenes (F10 §1 y regla 1): solo comprueba
que son las esperadas y las presenta a 1:1.
"""

from __future__ import annotations

import csv
import hashlib
import re
import struct
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

PATRON_ARCHIVO = re.compile(
    r"^MCv2_(?P<identidad>ID[12])_OJ(?P<OJ>peq|mae|gra)_PO(?P<PO>sub|bas|baj)"
    r"_CU(?P<CU>bas|lar)_v(?P<version>\d+)\.png$"
)
IDENTIDADES = ("ID1", "ID2")
NIVELES_OJ = ("peq", "mae", "gra")
NIVELES_PO = ("sub", "bas", "baj")
NIVELES_CU = ("bas", "lar")
COLUMNAS_MANIFIESTO = (
    "codigo", "archivo", "identidad", "OJ", "PO", "CU", "s", "yP_uc", "R",
    "ancho_px", "alto_px", "h_px", "sha256",
)


class ErrorEstimulos(Exception):
    """Los estímulos no coinciden con lo esperado. La sesión no debe empezar."""


@dataclass(frozen=True)
class Estimulo:
    codigo: str          # ID1-OJmae-PObas-CUbas
    archivo: str
    identidad: str
    OJ: str
    PO: str
    CU: str
    yP_uc: float
    ancho_px: int
    alto_px: int
    h_px: int
    sha256: str


@dataclass(frozen=True)
class Ensayo:
    ensayo_id: str
    tipo: str            # Crítico, Idéntico, Relleno
    par_id: str
    identidad: str       # ID1, ID2, Mixta
    rasgo: str           # OJ, PO, CU o –
    img_izq: str         # código de condición
    img_der: str


def codigo_desde_archivo(nombre: str) -> str:
    """MCv2_ID1_OJmae_PObas_CUbas_v5.png -> ID1-OJmae-PObas-CUbas (F10 §4.2)."""
    m = PATRON_ARCHIVO.match(nombre)
    if not m:
        raise ErrorEstimulos(f"Nombre de archivo fuera de la convención: {nombre}")
    return f"{m['identidad']}-OJ{m['OJ']}-PO{m['PO']}-CU{m['CU']}"


def niveles(codigo: str) -> dict[str, str]:
    identidad, oj, po, cu = codigo.split("-")
    return {"identidad": identidad, "OJ": oj, "PO": po, "CU": cu}


def codigos_esperados() -> list[str]:
    """Las 36 condiciones del diseño factorial (F10 §4.1 y Anexo A)."""
    return [
        f"{i}-OJ{oj}-PO{po}-CU{cu}"
        for i in IDENTIDADES for cu in NIVELES_CU for po in NIVELES_PO for oj in NIVELES_OJ
    ]


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with Path(ruta).open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


def tamano_png(ruta: Path) -> tuple[int, int]:
    """Lee ancho y alto de la cabecera IHDR sin depender de PIL."""
    with Path(ruta).open("rb") as f:
        cabecera = f.read(24)
    if cabecera[:8] != b"\x89PNG\r\n\x1a\n" or cabecera[12:16] != b"IHDR":
        raise ErrorEstimulos(f"No es un PNG válido: {ruta}")
    return struct.unpack(">II", cabecera[16:24])


def leer_manifiesto(ruta: Path) -> dict[str, Estimulo]:
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorEstimulos(f"No se encuentra el manifiesto: {ruta}")
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        faltan = [c for c in COLUMNAS_MANIFIESTO if c not in (lector.fieldnames or [])]
        if faltan:
            raise ErrorEstimulos(f"Faltan columnas en el manifiesto: {', '.join(faltan)}")
        estimulos = {}
        for fila in lector:
            e = Estimulo(
                codigo=fila["codigo"].strip(),
                archivo=fila["archivo"].strip(),
                identidad=fila["identidad"].strip(),
                OJ=fila["OJ"].strip(), PO=fila["PO"].strip(), CU=fila["CU"].strip(),
                yP_uc=float(fila["yP_uc"].replace(",", ".")),
                ancho_px=int(float(fila["ancho_px"])), alto_px=int(float(fila["alto_px"])),
                h_px=int(float(fila["h_px"])),
                sha256=fila["sha256"].strip().lower(),
            )
            if e.codigo in estimulos:
                raise ErrorEstimulos(f"Código repetido en el manifiesto: {e.codigo}")
            if codigo_desde_archivo(e.archivo) != e.codigo:
                raise ErrorEstimulos(f"El archivo {e.archivo} no corresponde al código {e.codigo}")
            estimulos[e.codigo] = e
    return estimulos


def verificar(
    carpeta: Path,
    manifiesto: dict[str, Estimulo],
    ancho_px: int,
    alto_px: int,
    comprobar_sha256: bool = True,
) -> None:
    """Prueba de aceptación 1 (F10 §11.2): 36 archivos, huellas y tamaño.

    Lanza ErrorEstimulos con todos los problemas encontrados, no solo el primero.
    """
    carpeta = Path(carpeta)
    problemas = []

    esperados = set(codigos_esperados())
    presentes = set(manifiesto)
    if presentes != esperados:
        if esperados - presentes:
            problemas.append("Faltan en el manifiesto: " + ", ".join(sorted(esperados - presentes)))
        if presentes - esperados:
            problemas.append("Sobran en el manifiesto: " + ", ".join(sorted(presentes - esperados)))

    for e in manifiesto.values():
        ruta = carpeta / e.archivo
        if not ruta.exists():
            problemas.append(f"Falta el archivo {e.archivo}")
            continue
        tam = tamano_png(ruta)
        if tam != (ancho_px, alto_px) or (e.ancho_px, e.alto_px) != (ancho_px, alto_px):
            problemas.append(
                f"{e.archivo}: mide {tam[0]} × {tam[1]} px; se esperaba {ancho_px} × {alto_px}"
            )
        if comprobar_sha256 and sha256_archivo(ruta) != e.sha256:
            problemas.append(f"{e.archivo}: la huella SHA-256 no coincide con el manifiesto")

    if problemas:
        raise ErrorEstimulos(
            "Los estímulos no superan la verificación; la sesión no puede empezar.\n- "
            + "\n- ".join(problemas)
        )


def leer_ensayos_fase1(ruta: Path) -> list[Ensayo]:
    with Path(ruta).open(encoding="utf-8-sig", newline="") as f:
        return [
            Ensayo(
                ensayo_id=fila["ensayo_id"], tipo=fila["tipo"], par_id=fila["par_id"],
                identidad=fila["identidad"], rasgo=fila["rasgo"],
                img_izq=fila["img_izq"], img_der=fila["img_der"],
            )
            for fila in csv.DictReader(f)
        ]


def verificar_composicion_fase1(ensayos: list[Ensayo]) -> None:
    """Prueba de aceptación 4: 28 críticos (cada par una vez con cada lado), 4 idénticos, 4 rellenos."""
    problemas = []
    tipos = Counter(e.tipo for e in ensayos)
    if len(ensayos) != 36:
        problemas.append(f"Hay {len(ensayos)} ensayos; deben ser 36")
    for tipo, n in (("Crítico", 28), ("Idéntico", 4), ("Relleno", 4)):
        if tipos.get(tipo, 0) != n:
            problemas.append(f"Hay {tipos.get(tipo, 0)} ensayos de tipo {tipo}; deben ser {n}")
    if len({e.ensayo_id for e in ensayos}) != len(ensayos):
        problemas.append("Hay ensayo_id repetidos")

    validos = set(codigos_esperados())
    for e in ensayos:
        for c in (e.img_izq, e.img_der):
            if c not in validos:
                problemas.append(f"{e.ensayo_id}: código desconocido {c}")

    criticos: dict[str, list[Ensayo]] = {}
    for e in ensayos:
        if e.tipo == "Crítico":
            criticos.setdefault(e.par_id, []).append(e)
    if len(criticos) != 14:
        problemas.append(f"Hay {len(criticos)} pares críticos; deben ser 14")
    for par, es in criticos.items():
        if len(es) != 2:
            problemas.append(f"El par {par} tiene {len(es)} ensayos; deben ser 2")
            continue
        a, b = es
        if (a.img_izq, a.img_der) != (b.img_der, b.img_izq) or a.img_izq == a.img_der:
            problemas.append(f"El par {par} no presenta cada imagen una vez a cada lado")
        else:
            diferencias = [k for k in ("OJ", "PO", "CU", "identidad")
                           if niveles(a.img_izq)[k] != niveles(a.img_der)[k]]
            if len(diferencias) != 1 or diferencias[0] != a.rasgo:
                problemas.append(f"El par {par} no difiere solo en el rasgo {a.rasgo}")

    for e in ensayos:
        if e.tipo == "Idéntico" and e.img_izq != e.img_der:
            problemas.append(f"{e.ensayo_id}: un ensayo idéntico debe mostrar la misma imagen")
        if e.tipo == "Relleno" and niveles(e.img_izq)["identidad"] == niveles(e.img_der)["identidad"]:
            problemas.append(f"{e.ensayo_id}: un relleno debe enfrentar ID1 con ID2")

    if problemas:
        raise ErrorEstimulos("La lista de duelos no cumple F10 §7.4:\n- " + "\n- ".join(problemas))
