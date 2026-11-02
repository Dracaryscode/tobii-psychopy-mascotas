"""Archivos de salida de cada sesión (F10 §10 y Anexo C).

Cada respuesta y cada evento se escriben y se vuelcan a disco en cuanto se
producen (regla 10), de modo que una interrupción no pierda datos.
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Columnas de respuestas.csv, en el orden del Anexo C (Tabla C1).
COLUMNAS_RESPUESTAS = (
    "participante", "sesion", "modo", "version_tarea", "fase", "n_global", "n_fase",
    "ensayo_id", "par_id", "tipo", "identidad", "rasgo", "img_izq", "img_der", "imagen",
    "OJ", "PO", "CU", "escala", "pregunta_id", "respuesta", "eleccion_codigo", "tr_ms",
    "t_onset_ms", "t_respuesta_ms", "intentos_fijacion", "respuestas_prematuras",
    "ventana_real_ms", "x_lienzo_izq", "y_lienzo_izq", "x_lienzo_der", "y_lienzo_der",
    "x_lienzo", "y_lienzo", "pct_muestras_validas", "et_valido",
)
COLUMNAS_EVENTOS = ("t_ms", "t_equipo_us", "evento", "fase", "n_global", "ensayo_id", "datos")
MODOS = ("real", "prueba", "automatico")
FASES = ("practica", "1", "2", "3", "4")


class ErrorRegistro(Exception):
    pass


class _CSV:
    """CSV que se vuelca a disco tras cada fila."""

    def __init__(self, ruta: Path, columnas: tuple[str, ...]):
        self.ruta = ruta
        self.columnas = columnas
        nuevo = not ruta.exists()
        self._f = ruta.open("a", encoding="utf-8", newline="")
        self._w = csv.DictWriter(self._f, fieldnames=columnas, extrasaction="raise")
        if nuevo:
            self._w.writeheader()
            self._volcar()

    def escribir(self, fila: dict[str, Any]) -> None:
        self._w.writerow({k: ("" if v is None else v) for k, v in fila.items()})
        self._volcar()

    def _volcar(self) -> None:
        self._f.flush()
        os.fsync(self._f.fileno())

    def cerrar(self) -> None:
        if not self._f.closed:
            self._f.close()


class Sesion:
    """Carpeta y archivos de una sesión: P001_S1_AAAAMMDD_HHMM/."""

    def __init__(
        self,
        carpeta_datos: Path,
        participante: str,
        sesion: int,
        modo: str,
        version_tarea: str,
        inicio: datetime | None = None,
    ):
        if modo not in MODOS:
            raise ErrorRegistro(f"Modo desconocido: {modo}")
        if not (len(participante) >= 2 and participante[0] == "P" and participante[1:].isdigit()):
            raise ErrorRegistro("El código de participante debe tener el formato P001")
        self.participante = participante
        self.sesion = sesion
        self.modo = modo
        self.version_tarea = version_tarea
        self.inicio = inicio or datetime.now()
        self._t0 = time.perf_counter()
        self.prefijo = f"{participante}_S{sesion}"
        self.carpeta = Path(carpeta_datos) / f"{self.prefijo}_{self.inicio:%Y%m%d_%H%M}"
        if self.carpeta.exists():
            raise ErrorRegistro(f"Ya existe la carpeta de la sesión: {self.carpeta}")
        self.carpeta.mkdir(parents=True)
        self.n_global = 0
        self._n_fase: dict[str, int] = {}
        self.et_valido = 0
        self.metadatos: dict[str, Any] = {
            "participante": participante,
            "sesion": sesion,
            "modo": modo,
            "version_tarea": version_tarea,
            "inicio": self.inicio.isoformat(timespec="seconds"),
            "fases": {},
            "pausas": [],
            "interrupciones": [],
        }
        self.respuestas = _CSV(self.ruta("respuestas.csv"), COLUMNAS_RESPUESTAS)
        self.eventos = _CSV(self.ruta("eventos.csv"), COLUMNAS_EVENTOS)
        self._log = self.ruta("registro.txt").open("a", encoding="utf-8")
        self.guardar_metadatos()

    def ruta(self, nombre: str) -> Path:
        return self.carpeta / f"{self.prefijo}_{nombre}"

    def t_ms(self) -> float:
        """Milisegundos desde el inicio de la sesión."""
        return round((time.perf_counter() - self._t0) * 1000, 3)

    def actualizar_metadatos(self, **datos: Any) -> None:
        self.metadatos.update(datos)
        self.guardar_metadatos()

    def guardar_metadatos(self) -> None:
        """Escritura atómica de sesion.json."""
        destino = self.ruta("sesion.json")
        tmp = destino.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(self.metadatos, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, destino)

    def respuesta(self, fase: str, **campos: Any) -> dict[str, Any]:
        """Escribe una fila de respuestas.csv; numera n_global y n_fase."""
        if fase not in FASES:
            raise ErrorRegistro(f"Fase desconocida: {fase}")
        desconocidas = set(campos) - set(COLUMNAS_RESPUESTAS)
        if desconocidas:
            raise ErrorRegistro(f"Columnas fuera del Anexo C: {', '.join(sorted(desconocidas))}")
        self.n_global += 1
        self._n_fase[fase] = self._n_fase.get(fase, 0) + 1
        fila = {c: None for c in COLUMNAS_RESPUESTAS}
        fila.update(
            participante=self.participante, sesion=self.sesion, modo=self.modo,
            version_tarea=self.version_tarea, fase=fase, n_global=self.n_global,
            n_fase=self._n_fase[fase], et_valido=self.et_valido,
        )
        fila.update(campos)
        self.respuestas.escribir(fila)
        return fila

    def evento(self, evento: str, fase: str = "", n_global: int | None = None,
               ensayo_id: str = "", t_equipo_us: int | None = None, **datos: Any) -> None:
        self.eventos.escribir({
            "t_ms": self.t_ms(), "t_equipo_us": t_equipo_us, "evento": evento, "fase": fase,
            "n_global": n_global, "ensayo_id": ensayo_id,
            "datos": json.dumps(datos, ensure_ascii=False) if datos else "",
        })

    def log(self, mensaje: str) -> None:
        self._log.write(f"{datetime.now().isoformat(timespec='seconds')}\t{self.t_ms():.0f}\t{mensaje}\n")
        self._log.flush()
        os.fsync(self._log.fileno())

    def interrupcion(self, motivo: str) -> None:
        self.metadatos["interrupciones"].append({"t_ms": self.t_ms(), "motivo": motivo})
        self.guardar_metadatos()
        self.log(f"INTERRUPCION: {motivo}")

    def cerrar(self) -> None:
        self.metadatos["fin"] = datetime.now().isoformat(timespec="seconds")
        self.guardar_metadatos()
        self.respuestas.cerrar()
        self.eventos.cerrar()
        if not self._log.closed:
            self._log.close()
