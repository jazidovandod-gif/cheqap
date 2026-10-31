# Declaración de material previo

El sprint puntúa el avance durante el bloque de trabajo (09:00 a 16:00 del 31 de octubre de 2026). Esto es lo que existía antes.

## Antes de las 09:00

- La idea: verificar afirmaciones de un chatbot contra un PDF y medirlo con un benchmark en español y aymara.
- Un plan escrito (este `docs/PLAN.md` en su primera versión, sin código).
- Ningún archivo de código, ningún ítem etiquetado, ningún resultado.

## Hecho durante el sprint

Completar al cierre:

- Código en `consta/`, `app/`, `benchmark/`.
- Ítems etiquetados en `data/benchmark/` (commit `____`).
- Resultados en `results/` (commit `____`).

## Material de terceros usado

- PDF fuente: Ley N° 453, Ley general de los derechos de las usuarias y los usuarios y de las consumidoras y los consumidores (15 páginas). Copia del Compendio del Servicio de Evaluación de Aduanas: https://sea.gob.bo/digesto/CompendioII/J/77_L_453.pdf. Texto oficial: Gaceta Oficial del Estado Plurinacional, https://www.gacetaoficialdebolivia.gob.bo/normas/verGratis_gob/147245. Nota: la cabecera del compendio dice «5 de Febrero de 2013», pero el texto de la ley dice que fue promulgada el 4 de diciembre de 2013; el benchmark no usa esa fecha.
- AmericasNLI, corte `aym`, 30 pares del split `dev`. Ebrahimi et al., ACL 2022. Revisar licencia del dataset antes de redistribuir las filas; si no permite, dejar solo el script que las descarga.
- Librerías: ver `requirements.txt`.
