# Bambu Lab A1 — máquina y materiales (conocimiento de maestro)

Índice: 1. La máquina · 2. Placas · 3. Materiales uno a uno · 4. Secado · 5. AMS lite y multicolor · 6. Calibraciones

Números exactos por perfil → `perfiles_oficiales_a1.md`. Aquí va el *porqué* y los trucos.

---

## 1. La máquina (lo que condiciona cada decisión)

| Dato | Valor | Consecuencia práctica |
|---|---|---|
| Volumen | 256 × 256 × 256 mm | Deja ~2 mm de margen. La diagonal de la cama (~360 mm) permite piezas largas en diagonal. |
| Cinemática | **Bed slinger**: la cama se mueve en **Y**, el cabezal en X/Z | Piezas altas y esbeltas se tambalean o despegan por la inercia de la cama. La pieza "látigo" sufre en Y. |
| Marco | **Abierto**, sin cerramiento | ABS/ASA/PC/PA: warping y peor unión entre capas en piezas grandes/rellenas. Corrientes de aire importan. |
| Boquilla | Acero inoxidable 0.4 de serie (hay 0.2 / 0.6 / 0.8). Máx **300 °C** | Filamentos con fibra (CF/GF) o glow/abrasivos → **boquilla de acero endurecido** (el inox se come en horas). |
| Cama | Máx **100 °C** | ABS/ASA/PC justos: sin cerramiento, piezas pequeñas-medianas. |
| Velocidad / aceleración | 500 mm/s, 12 000 mm/s² (Sport/Turbo en pantalla) | El límite real casi siempre es el **caudal volumétrico** del filamento (mm³/s), no la velocidad. |
| Extrusor | Directo | Maneja TPU 90A+ bien (por bobina externa). |
| Holgura por objeto | `extruder_clearance_height_to_rod` = **25 mm**, radio 57 mm | "Imprimir por objeto" solo con piezas ≤ 25 mm de alto (la última puede ser más alta). |
| Autocalibración | Nivelado de cama, compensación de vibración (resonancia), dinámica de flujo (pressure advance), Z-offset — **cada impresión** | Z-offset casi nunca se toca. Activar "Flow dynamics calibration" con filamentos nuevos, silk, PETG, TPU. |
| Cortador + purga | Cortador de filamento y purga trasera (sin torre en cambios manuales) | Con AMS lite la torre de purga viene activa (`enable_prime_tower=1`). |
| Modos velocidad | Silent 50 %, Standard 100 %, Sport 124 %, Ludicrous 166 % | Silent ayuda a piezas altas/esbeltas y a calidad de superficie sin re-laminar. |

**Ralentización por altura (exclusiva y útil en A1)**: claves `enable_height_slowdown`, `slowdown_start_height`, `slowdown_end_height`, `slowdown_start_speed`, `slowdown_end_speed`, `slowdown_start_acc`, `slowdown_end_acc`. Interpolan la velocidad/aceleración máxima según la altura: justo lo que pide una pieza alta en bed slinger. Valida siempre con el slicer (sube el tiempo).

## 2. Placas (build plates)

Temperaturas por material → tabla de filamentos (columnas Textured / Smooth PEI / Cool / SuperTack / Eng). **0 = el perfil no recomienda esa placa.**

| Placa | Clave `curr_bed_type` | Mejor para | Trucos |
|---|---|---|---|
| **Textured PEI** (la de serie en A1) | `Textured PEI Plate` | PLA, PETG, ABS/ASA, TPU, PC | Cara inferior con textura granulada, esconde imperfecciones. Adhesión menor en piezas con poca huella → brim. Limpiar con **agua caliente + jabón de platos** (no solo alcohol). Sin tocar con dedos. |
| **Smooth PEI / High Temp** | `High Temp Plate` | PLA, ABS, PC; cara inferior brillante | **PETG y TPU se pegan demasiado → arrancan el PEI**. Usar pegamento en barra como *separador* con PETG/TPU. Limpiar con IPA. |
| **Cool Plate SuperTack** | `Supertack Plate` | PLA (35–45 °C), PETG, TPU | Agarre enorme sin pegamento, cama fría = menos pata de elefante. Ideal piezas con poca huella. |
| **Cool Plate** (clásica) | `Cool Plate` | PLA, TPU a baja temp | Requiere pegamento. No para PETG. |
| **Engineering** | `Engineering Plate` | ABS/ASA/PC/PA/PETG con pegamento | Siempre con pegamento. |

Regla de oro: la placa **física** debe coincidir con la elegida en el slicer (si no, temperatura de cama errónea → despegues). Dilo explícitamente en la salida.

## 3. Materiales uno a uno

### PLA (Basic, Matte, Silk, Tough, Lite, Metal, Marble, Sparkle, Galaxy, Glow, Aero, Dynamic)
- Perfil A1 PLA Basic: 220 °C, cama 65 °C (Textured/Smooth), 35 °C Cool, 45 °C SuperTack, fan 60–80 %, **21 mm³/s**.
- Fácil, casi no deforma. **Tg ≈ 45–55 °C**: no para coche al sol, cerca de motores, lavavajillas.
- **Silk / Silk+**: caudal bajo (~12 mm³/s), menos fan en voladizos gruesos, piezas más débiles entre capas; muy vistoso con 1 pared exterior limpia. Activar flow dynamics.
- **Matte**: capa inferior se agarra peor → brim si huella pequeña. Esconde líneas de capa.
- **PLA-CF / Glow / Marble / Sparkle / Metal**: abrasivos → boquilla endurecida recomendable.
- **Tough/Tough+**: más tenaz (menos frágil), algo más de temp.
- **Aero (espumado)**: temps y caudal distintos, usar su perfil, sin mezclar.
- Warping grande (piezas planas >150 mm): cama 65 °C primera capa, brim, sin fan 2–3 capas, evitar corrientes, esquinas redondeadas.

### PETG (Basic, HF, Matte, Translucent, CF)
- HF: 240 °C (230 primera capa), cama 70 °C, fan **30–50 %**, 18 mm³/s. Basic: 245 °C, 13 mm³/s, 12 s tiempo mínimo de capa.
- **Mala adhesión con Smooth PEI (demasiada)** → pegamento como barrera. En Textured PEI va bien directo.
- Cuerdas (stringing) y gotas: secar (65 °C 8 h), `z_hop` moderado, retracción del perfil, bajar temp 5 °C, desactivar "wipe" no suele hacer falta. Menos fan que PLA para buena unión entre capas; más fan si hay voladizos/puentes.
- Mejor que PLA para exterior, temperatura (~70–80 °C), tenacidad. Ligeramente más flexible.
- Tolerancias: PETG "se engorda" un poco → +0.05 mm de holgura extra vs PLA.

### ABS / ASA
- 260–270 °C, cama **90–100 °C**, fan 10–35 %.
- En A1 (abierto): piezas pequeñas-medianas; huella grande o 100 % relleno → warping y grietas entre capas. Mitigar: brim 5–8 mm (`brim_type=outer_only`), `draft_shield=enabled` (escudo contra corrientes), sin fan primeras 3 capas, habitación sin corrientes, esquinas redondeadas, relleno ≤ 20 %.
- ASA > ABS para exterior (UV). Olor/VOC: ventilar.
- Si la pieza es grande y funcional, **proponer PETG/PETG-CF o PLA Tough** como alternativa honesta.

### PC / PA / PA-CF / PAHT / PET-CF / PPA
- Perfiles existen para A1 pero con advertencia oficial: marco abierto = peor unión y warping. PA muy higroscópico (secar 80–90 °C 12 h+ y imprimir desde secador). CF/GF → boquilla endurecida. Engineering/Smooth PEI + pegamento. Solo piezas pequeñas y justificadas.

### TPU (85A, 90A, 95A, HF)
- Perfil A1 TPU 90A: 225 °C, cama 30–45 °C, **2.8 mm³/s** (lentísimo a propósito), fan 100 %.
- **Bobina externa**, no por AMS lite. Secar (TPU absorbe agua → burbujas/cuerdas).
- Imprimir despacio, sin retracciones largas, `z_hop` bajo, relleno gyroid 10–25 % para amortiguación, paredes ≥ 3 para estanqueidad.
- Smooth PEI → pegamento (se funde con la placa). Textured o SuperTack mejor.
- 85A extra blando: riesgo de atasco; bajar aún más caudal.

### Soportes solubles / de interfaz
- `Bambu Support For PLA/PETG`: material de interfaz para despegar limpio (con AMS lite): usar solo en la **interfaz** (`support_interface_filament`) y poner `support_top_z_distance=0`.
- PVA: soluble en agua, muy higroscópico. PLA como interfaz para PETG y PETG para PLA funciona (no se pegan entre sí) — truco barato con AMS.

## 4. Secado (antes de culpar al slicer)
| Material | Temp | Tiempo |
|---|---|---|
| PLA | 50–55 °C | 6–8 h |
| PETG | 65 °C | 8 h |
| ABS/ASA | 80 °C | 8 h |
| TPU | 65–70 °C | 8 h |
| PC | 80 °C | 8 h |
| PA/PA-CF | 80–90 °C | 12 h+ |
| PVA | 55 °C | 8 h+ |
Síntomas de humedad: chasquidos, burbujas, cuerdas, superficie rugosa/opaca, capas débiles.

## 5. AMS lite y multicolor
- 4 bobinas. Cada cambio de color = purga. Reducir desperdicio: "Flush into object's infill" / "Flush into objects' support", multiplicador de purga 0.6–0.8 (validar color claro después de oscuro), imprimir varias copias por placa (la purga se reparte), agrupar colores en capas concretas.
- Torre de purga (`prime_tower_width` 35 mm por defecto) ocupa cama: ubicarla lejos de piezas altas.
- TPU y filamentos muy frágiles/blandos → bobina externa.

## 6. Calibraciones que el usuario puede hacer (recomendar solo si aporta)
- **Flow dynamics** (pressure advance): automática en A1 si se marca en el diálogo de impresión; manual en Calibration para filamentos de terceros.
- **Flow rate** (Calibration → Flow rate): si superficies superiores con huecos o sobreextrusión.
- **Temperatura (torre)**: filamentos de terceros.
- **Max volumetric speed**: si un filamento de terceros subextruye a alta velocidad.
- **Tolerancias**: imprimir test de holguras propio si el usuario hace encajes a menudo.
