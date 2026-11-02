# Mascotas científicas: tarea experimental

Tarea de laboratorio con eye tracking para estudiar cómo tres cambios en el dibujo de un gato (tamaño de los ojos, altura de los ojos y longitud del cuerpo) modifican la ternura percibida.

- **Investigadora responsable:** Alison Geraldine Quiroz Quispe (Neurolab, Universidad de Lima).
- **Desarrollo:** Kevin.
- **Especificación:** [documento maestro F10](docs/diseno/F10_Documento_maestro_tarea_experimental_ingeniero_v1.md). Es la fuente de verdad del programa; el código sigue sus reglas al pie de la letra.
- **Equipo:** Tobii Pro Fusion (250 Hz) con TittaPy y PsychoPy.

## Sesión

práctica de duelos → calibración → **fase 1** duelos (36) → práctica + **fase 2** ternura (36) → práctica + **fase 3** agrado y edad (36 × 2) → práctica + **fase 4** extrañeza (36) → cierre

El orden es fijo para todos los participantes. Los duelos se aleatorizan con dos restricciones: el mismo par nunca va en dos ensayos seguidos, y no puede haber más de tres seguidos del mismo gato. La semilla se genera al iniciar la sesión y se guarda.

## Estructura

```
config/          parametros.yaml (Tabla 9 de F10), textos.yaml (§7 y Anexo D), cierre.yaml
diseno/          ensayos_fase1.csv: los 36 duelos antes de aleatorizar (Anexo B)
docs/diseno/     documentos de la investigadora: F10 (.md, .docx y figuras), F12 (.xlsx) y CSV original
docs/            decisiones.md: registro de cambios respecto de F10
estimulos/       imágenes (no se versionan; ver estimulos/LEEME.md)
src/mascotas/    código
  config.py          carga y valida la configuración
  estimulos.py       códigos, manifiesto, SHA-256, lista de duelos
  aleatorizacion.py  semilla y órdenes de las cuatro fases
  disposicion.py     coordenadas de lienzos, cruz y AOIs
  registro.py        archivos de salida (Anexo C) con escritura inmediata
  preparacion.py     todo lo que se comprueba antes de empezar
tests/           pruebas de aceptación de F10 §11.2 que no necesitan pantalla
run.py           punto de entrada
datos/           salidas de las sesiones (no se versiona)
```

## Uso

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python -m pytest                          # pruebas
python run.py verificar                   # comprueba estímulos y configuración
python run.py ordenes --semilla 123       # muestra los órdenes que tocarían con esa semilla
```

## Estado

| Paso del plan | Estado |
|---|---|
| 1. Estructura, configuración y textos | ✅ |
| 2. Estímulos (manifiesto, SHA-256) y aleatorización. Pruebas 1, 4, 5, 6 | ✅ |
| 3. Registro de datos (Anexo C) | ✅ (falta conectarlo a las fases) |
| 4. Fases con PsychoPy en modo prueba y automático. Pruebas 10, 12, 13, 14 | Pendiente |
| 5. Tobii con TittaPy: calibración, control de fijación, eventos, muestras. T3 | Pendiente |
| 6. Pruebas en el laboratorio: 2, 3, 8, 9, 15 | Pendiente |

El código del diseño anterior (T1/T2) está en la rama `legacy-T1-T2`.
