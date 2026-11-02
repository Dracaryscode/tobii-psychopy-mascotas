# Instrucciones para trabajar en este repositorio

- La especificación es `docs/diseno/F10_Documento_maestro_tarea_experimental_ingeniero_v1.md`. Síguela al pie de la letra. Lo marcado [D] no se cambia sin autorización de la investigadora; lo [P] y [X] va en `config/parametros.yaml`, nunca fijo en el código.
- Toda desviación de F10 se anota en `docs/decisiones.md`.
- Los textos para el participante solo viven en `config/textos.yaml` y se reproducen literalmente.
- Las imágenes se muestran a 1:1, sin reescalar (regla 1). Si no caben, se regeneran; el programa no las transforma.
- Nada de `hash()` para la aleatorización: usa `aleatorizacion.generador(semilla, uso)`.
- Antes de cambiar una interfaz entre módulos, busca todos sus usos y actualízalos en el mismo cambio, con sus tests. Ejecuta `python -m pytest` antes de cada commit.
- Python 3.10 (el entorno del laboratorio): no uses sintaxis posterior.
