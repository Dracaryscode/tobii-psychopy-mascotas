"""
registro.py — Registro de eventos y archivos de salida por participante.

SEGURIDAD DE DATOS:
    - Cada fila se escribe y se vacía (flush) inmediatamente al disco.
      Si el experimento se interrumpe, los datos hasta ese punto quedan guardados.
    - verificar_no_duplicado() aborta antes de abrir la ventana si el participante
      ya tiene un archivo CSV: los participantes no pueden repetir la prueba.
    - El HDF5 de la mirada (ioHub) se guarda en la misma carpeta.

Columnas del CSV:
    timestamp_exp_s  — tiempo del reloj del experimento (s)
    hora_real        — hora del reloj de pared (ISO 8601)
    tarea            — tarea1 | tarea2 | setup | fin
    n_ensayo         — número de ensayo dentro de la tarea (vacío si no aplica)
    repeticion       — número de repetición (vacío si no aplica)
    grupo            — grupo del estímulo (Ojos / Cabeza / Triangulo; vacío en T2)
    variante         — variante concreta del estímulo
    aoi              — área(s) de interés definida(s) para el estímulo
    evento           — fijacion_on/off, estimulo_on/off, instruccion, pausa, etc.
    estimulo         — nombre lógico del/los estímulo(s)
    posicion         — posición en pantalla
    info_extra       — JSON con datos adicionales (p. ej. rutas de archivo)
"""

import csv
import json
from datetime import datetime
from pathlib import Path

from . import config


CAMPOS = [
    "timestamp_exp_s",
    "hora_real",
    "tarea",
    "n_ensayo",
    "repeticion",
    "grupo",
    "variante",
    "aoi",
    "evento",
    "estimulo",
    "posicion",
    "info_extra",
]


class RegistroParticipante:

    def __init__(self, participante: str):
        self.participante = participante
        self.carpeta  = config.DATOS_DIR / participante
        self.ruta_csv = self.carpeta / f"eventos_{participante}.csv"
        self.ruta_hdf5 = self.carpeta / f"mirada_{participante}.hdf5"
        self._n_filas  = 0
        self._fh       = None
        self._writer   = None

    # ------------------------------------------------------------------
    # Control del archivo
    # ------------------------------------------------------------------

    def verificar_no_duplicado(self) -> None:
        """Lanza ValueError si ya existen datos para este participante."""
        if self.ruta_csv.exists():
            raise ValueError(
                f"\n{'='*60}\n"
                f"  ERROR: El participante '{self.participante}' ya tiene datos.\n"
                f"  Archivo: {self.ruta_csv}\n"
                f"  Usa un ID diferente o verifica que no sea un error.\n"
                f"{'='*60}\n"
            )

    def iniciar(self) -> None:
        """Abre el CSV y escribe la cabecera. Llamar una sola vez."""
        self.carpeta.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.ruta_csv, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fh, fieldnames=CAMPOS)
        self._writer.writeheader()
        self._fh.flush()

    def cerrar(self) -> None:
        """Cierra el archivo de forma limpia."""
        if self._fh and not self._fh.closed:
            self._fh.flush()
            self._fh.close()

    # ------------------------------------------------------------------
    # Registro de eventos
    # ------------------------------------------------------------------

    def log(self, t, tarea, evento, *, n_ensayo="", repeticion="",
            grupo="", variante="", aoi="", estimulo="", posicion="",
            extra=None) -> None:
        """Registra un evento y lo escribe inmediatamente al disco."""
        if self._writer is None:
            raise RuntimeError("Llama a iniciar() antes de log().")
        fila = {
            "timestamp_exp_s": round(float(t), 4),
            "hora_real":        datetime.now().isoformat(timespec="milliseconds"),
            "tarea":            tarea,
            "n_ensayo":         n_ensayo,
            "repeticion":       repeticion,
            "grupo":            grupo or "",
            "variante":         variante or "",
            "aoi":              aoi or "",
            "evento":           evento,
            "estimulo":         estimulo,
            "posicion":         posicion,
            "info_extra":       json.dumps(extra, ensure_ascii=False) if extra else "",
        }
        self._writer.writerow(fila)
        self._fh.flush()   # escritura inmediata — datos seguros ante fallos
        self._n_filas += 1

    def log_ensayo(self, t, ensayo: dict, evento: str) -> None:
        """Atajo: registra un evento con todos los datos del ensayo actual."""
        nombres    = " | ".join(e["nombre"]   for e in ensayo["estimulos"])
        posiciones = " | ".join(e["posicion"] for e in ensayo["estimulos"])
        self.log(
            t, ensayo["tarea"], evento,
            n_ensayo=ensayo["n_ensayo"],
            repeticion=ensayo["repeticion"],
            grupo=ensayo.get("grupo") or "",
            variante=ensayo.get("variante") or "",
            aoi=ensayo.get("aoi") or "",
            estimulo=nombres,
            posicion=posiciones,
            extra={"archivos": [e["archivo"] for e in ensayo["estimulos"]]},
        )

    @property
    def n_eventos(self) -> int:
        return self._n_filas
