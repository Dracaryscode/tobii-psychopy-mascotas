# Experimento Mascotas — Presentación + Eye Tracking (Tobii Pro Fusion)

Programa que **presenta la prueba a cada participante** mientras el **Tobii Pro
Fusion** graba la mirada. El análisis de los datos es un paso posterior y
separado (este programa solo presenta y graba).

Construido con **PsychoPy** (presentación, timing, calibración) +
**Tobii Pro SDK** (`tobii_research`) vía ioHub.

---

## Estructura

```
experimento_mascotas/
├── run_experimento.py      ← EJECUTAR por participante (necesita PsychoPy + Tobii)
├── run_simulacion.py       ← PROBAR sin hardware (cualquier laptop)
├── generar_placeholders.py ← crea imágenes de prueba
├── requirements.txt
├── README.md
│
├── src/
│   ├── config.py        parámetros: tiempos, pantalla, estímulos, posiciones
│   ├── secuencia.py     genera la secuencia de ensayos (randomización/contrabalanceo)
│   ├── registro.py      log de eventos + archivos por participante
│   ├── tracker.py       conexión / calibración / grabación Tobii (ioHub)
│   ├── pantallas.py     instrucciones, fijación, pausas
│   └── tareas.py        rutinas de presentación de las 3 tareas
│
├── estimulos/
│   ├── tarea1/   ← 5 mascotas individuales (PNG/JPG)
│   ├── tarea2/   ← 9 imágenes de características
│   └── tarea3/   ← 3 variantes completas
│
├── datos/        ← salida: una carpeta por participante
│   └── <ID>/
│       ├── mirada_<ID>.hdf5     (mirada cruda, la graba ioHub)
│       └── eventos_<ID>.csv     (marcas de cada ensayo)
│
└── tests/        ← pruebas de la secuencia (pytest)
```

---

## Las 3 tareas (según los documentos)

| Tarea | Estímulos | Ensayos | Tiempo/ensayo | Total |
|---|---|---|---|---|
| **1 — Exploración libre** | 5 mascotas, una a una | 5×5 = 25 | 5 s | ~2 min |
| **2 — Características** (pares 2×2) | 3 grupos × 3 pares | 9×5 = 45 | 10 s* | ~7.5 min |
| **3 — Totalidad** | 3 variantes a la vez | 3×5 = 15 | 1 s fijación + 10 s | ~2.5 min |

\* La duración por ensayo de la Tarea 2 no aparece en el documento; se derivó
del total (~7.5 min ÷ 45 ensayos = 10 s). Ajustable en `src/config.py`.

> **Nota sobre la Tarea 1 y el TTFF:** el documento no incluye una fijación
> central antes de cada mascota, así que está en 0. Como la hipótesis usa el
> *Time to First Fixation*, conviene una fijación de 1 s para fijar el punto de
> partida. Si la quieres, cambia `fijacion_s` de `tarea1` a `1.0` en `config.py`.

---

## 1. Probar SIN hardware (recomendado antes de ir al laboratorio)

No necesita PsychoPy ni el Tobii. Verifica secuencia, tiempos y formato de salida:

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
python run_simulacion.py P01
```

Y las pruebas automáticas:

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## 2. Preparar el laboratorio (máquina con el Tobii)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> En el laboratorio, PsychoPy se suele instalar como **PsychoPy Standalone**
> (incluye todo). Si usas pip, asegúrate de que `tobii_research` instale bien
> (es el Tobii Pro SDK oficial; soporta el Pro Fusion).

### Estímulos

Coloca las imágenes reales en `estimulos/tarea1`, `tarea2`, `tarea3` con los
nombres de archivo definidos en `src/config.py`.
¿Aún no tienes el arte final? Genera placeholders:

```bash
python generar_placeholders.py
```

### Calibrar el monitor (importante)

Antes de correr, define tu monitor en el **Monitor Center** de PsychoPy con el
nombre `monitor_lab` (o cambia `MONITOR_NOMBRE` en `config.py`), indicando
tamaño en cm, resolución y distancia (~65 cm). Esto es necesario para que las
coordenadas de la mirada y las AOIs sean correctas.

---

## 3. Ejecutar con un participante

```bash
python run_experimento.py P01
```

El programa: bienvenida → calibración del Tobii (9 puntos) →
Tarea 1 → pausa → Tarea 2 → pausa → Tarea 3 → fin.
Pulsa **ESC** en cualquier momento para abortar (guarda lo registrado).

### Salida (en `datos/P01/`)

- `mirada_P01.hdf5` — mirada cruda grabada por ioHub (todos los samples a 250 Hz).
- `eventos_P01.csv` — una fila por evento (inicio/fin de fijación y de estímulo),
  con marca de tiempo, tarea, nº de ensayo, estímulo y posición.

Para el **análisis posterior**, los marcadores enviados al Tobii y el CSV de
eventos te permiten segmentar la mirada por ensayo y por estímulo, y luego
definir las AOIs (Ojos, Nariz, Boca, Cuerpo) sobre cada imagen.

---

## Cómo cambiar cosas

| Quiero… | Dónde |
|---|---|
| Cambiar tiempos por tarea | `src/config.py` → `TIEMPOS` |
| Cambiar nº de repeticiones | `src/config.py` → `REPETICIONES` |
| Cambiar/añadir mascotas o niveles | `src/config.py` → diccionarios de estímulos |
| Cambiar posiciones/tamaños en pantalla | `src/config.py` → sección DISPOSICIÓN |
| Cambiar textos de instrucciones | `src/pantallas.py` → `INSTRUCCIONES` |
| Cambiar la lógica de aleatorización | `src/secuencia.py` |
