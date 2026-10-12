# Uso de los scripts

Ejemplos desde la carpeta instalada de la skill. Usa el Python de tu entorno virtual.

## Analizar

```bash
python scripts/analyze_models.py "/ruta/a/modelos" --top 3 --threshold 45
```

El recorrido de carpetas es recursivo. Excluye `_analisis_a1` y la carpeta `--out` elegida. Los nombres llevan un identificador derivado de la ruta para evitar colisiones entre piezas homónimas. No se escribe sobre modelos originales. Los informes contienen rutas locales: revísalos antes de compartirlos.

`--threshold` está entre 0 y 90 grados (excluidos); `--top` entre 1 y 12. Los gramos del informe geométrico son aproximaciones, no el consumo del laminador.

## Laminar

```bash
python scripts/bambu_slice.py --list process
python scripts/bambu_slice.py --list filament PETG
python scripts/bambu_slice.py --show filament "Bambu PETG HF" --keys nozzle_temperature,fan_max_speed
python scripts/bambu_slice.py "/ruta/orientado.stl" --process "0.20mm Standard" --filament "Bambu PLA Basic" --plate textured --set wall_loops=3 --outdir "/ruta/_analisis_a1/slice_base"
```

Varios modelos se colocan en una misma placa. La orientación se conserva salvo que pases `--orient`. `--keep` conserva el G-code; de lo contrario se elimina junto con los archivos temporales al terminar normalmente. `--timeout` limita el laminado (900 s por defecto).

Los valores desconocidos de `--set` se rechazan. `OVERRIDE_MISMATCH` significa que los ajustes efectivos del G-code no coinciden o no se pueden comprobar: corrige la clave/valor y relamina antes de recomendar la variante. Guarda cada variante en un `--outdir` distinto.

## Diagnóstico local

```bash
python scripts/check_environment.py
```

Devuelve una lista JSON con `ok` por requisito. No consulta Google. `npx … doctor` añade las comprobaciones de skill y CLI, y devuelve código 1 si faltan requisitos. La consulta de autenticación solo se hace con `--check-auth`.

## Códigos de salida

| Script | Código | Significado |
| --- | --- | --- |
| analyze_models.py | 0 | Todos los modelos analizados |
| analyze_models.py | 1 | Sin modelos o algún modelo falló; revisa report.json |
| analyze_models.py | 2 | Argumentos o dependencias inválidos |
| bambu_slice.py | 0 | Consulta de perfiles correcta o laminado validado |
| bambu_slice.py | 1 | Error de laminado/perfiles/ejecución |
| bambu_slice.py | 2 | Argumentos inválidos o OVERRIDE_MISMATCH |
| bambu_slice.py | 3 | Bambu Studio o perfiles no encontrados |

Los scripts nunca consultan NotebookLM directamente: esa fase la ejecuta el agente según `SKILL.md`.
