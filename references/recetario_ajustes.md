# Recetario: de lo que ves en la geometría → ajuste exacto de Bambu Studio

Cada ajuste lleva: **pestaña de Bambu Studio** (UI en inglés / español) · **clave** para `bambu_slice.py --set clave=valor` · valor. Todas las claves de esta tabla han sido probadas en el CLI de Bambu Studio 2.x y aparecen en el gcode resultante.

Índice: 1. Mapa pestañas · 2. Elegir perfil base · 3. Recetas por situación · 4. Enumerados válidos · 5. Solución de problemas

---

## 1. Mapa de pestañas (Process)
| Pestaña EN / ES | Claves habituales |
|---|---|
| Quality / Calidad | `layer_height`, `initial_layer_print_height`, `line_width`, `seam_position`, `seam_slope_type` (scarf), `wall_generator`, `detect_thin_wall`, `ironing_type`, `xy_hole_compensation`, `xy_contour_compensation`, `elefant_foot_compensation`, `enable_circle_compensation`, `precise_outer_wall`, `only_one_wall_top`, `resolution` |
| Strength / Resistencia | `wall_loops`, `top_shell_layers`, `bottom_shell_layers`, `top_shell_thickness`, `sparse_infill_density`, `sparse_infill_pattern`, `top_surface_pattern`, `infill_wall_overlap` |
| Speed / Velocidad | `outer_wall_speed`, `inner_wall_speed`, `sparse_infill_speed`, `initial_layer_speed`, `default_acceleration`, `outer_wall_acceleration`, `enable_overhang_speed`, `bridge_speed`, `enable_height_slowdown` + `slowdown_*` |
| Support / Soporte | `enable_support`, `support_type`, `support_threshold_angle`, `support_on_build_plate_only`, `support_top_z_distance`, `support_interface_top_layers`, `support_object_xy_distance`, `support_interface_filament` |
| Others / Otros | `brim_type`, `brim_width`, `brim_object_gap`, `skirt_loops`, `draft_shield`, `print_sequence`, `spiral_mode` (vase), `fuzzy_skin`, `enable_prime_tower`, `flush_into_infill` |
| Filament (ajustes del filamento) | `nozzle_temperature`, `nozzle_temperature_initial_layer`, `textured_plate_temp` / `hot_plate_temp` / …, `fan_min_speed`, `fan_max_speed`, `overhang_fan_speed`, `close_fan_the_first_x_layers`, `filament_max_volumetric_speed`, `slow_down_layer_time`, `filament_retraction_length` |

## 2. Elegir perfil de proceso base (A1, boquilla 0.4)
| Objetivo | Perfil base | Notas |
|---|---|---|
| Uso general, prototipo | `0.20mm Standard` | Defecto. 2 paredes, 15 % grid. |
| Funcional / mecánica | `0.20mm Strength` | 6 paredes, 25 %, pared exterior lenta. O Standard + `wall_loops=4`. |
| Bonito, curvas suaves, figuras | `0.16mm High Quality` / `0.12mm High Quality` | Exterior a 60 mm/s y aceleración 2000: menos ringing. |
| Equilibrio calidad/tiempo | `0.16mm Optimal` | Rápido pero con capa fina. |
| Miniaturas, texto pequeño | `0.08mm High Quality` o boquilla 0.2 | Muy lento; vale la pena solo si el detalle < 0.5 mm importa. |
| Rápido y grande, poca estética | `0.24mm Draft` / `0.28mm Extra Draft` | Mejor unión entre capas, menos tiempo. |
| Piezas grandes rápidas | Boquilla 0.6 (0.30mm Standard) | Recomiéndala si la pieza es grande y el detalle no importa. |

Capas: la altura debe ser ≤ ~75 % del diámetro de boquilla (0.4 → máx 0.28–0.30). Si las cotas en Z importan (p.ej. una pieza de 9 mm), elige una altura que divida la altura total o acepta ±½ capa.

## 3. Recetas por situación

| Situación detectada | Ajuste (clave=valor) | Por qué |
|---|---|---|
| Paredes < 0.8 mm (informe) | `wall_generator=arachne`, `detect_thin_wall=1` | Arachne varía el ancho de línea y no pierde paredes finas. |
| Paredes < 0.45 mm | Boquilla 0.2 o avisar que no saldrán | 0.4 no puede extruir menos de ~0.4 mm. |
| Pieza funcional (clips, soportes, ganchos) | `wall_loops=4`, `sparse_infill_density=25%`, `sparse_infill_pattern=gyroid` (o `cubic`), `top_shell_layers=5`, `bottom_shell_layers=4` | Resistencia en paredes; relleno isótropo. |
| Clip / pestaña flexible | Orientar para que la flexión vaya en el plano XY; `wall_loops=3–4`; PETG o PLA Tough mejor que PLA | Evita romper entre capas. |
| Agujeros de precisión verticales | `xy_hole_compensation=0.1` (o `enable_circle_compensation=1`) | Compensa el encogimiento típico de agujeros. |
| Encaje por la base / cotas en primera capa | `elefant_foot_compensation=0.15` | Evita la pata de elefante. |
| Poco contacto con la cama (< ~150 mm² o esbeltez > 2.5) | `brim_type=outer_only`, `brim_width=5` (8 si alta), `brim_object_gap=0.1` | Evita despegues. En piezas pequeñas con esquinas: `brim_type=brim_ears`. |
| Pieza alta y esbelta (esbeltez > 3) | Brim + `enable_height_slowdown=1`, `slowdown_start_height=<≈40 % altura>`, `slowdown_end_height=<altura>`, `slowdown_end_speed=100`, `slowdown_end_acc=2000` | Bed slinger: reduce latigazo en Y. |
| Cara superior grande y visible | `ironing_type=top` (solo capa superior), o `top_surface_pattern=monotonicline` (defecto) | Planchado = superficie lisa; +tiempo. No en superficies curvas ni con texto hundido. |
| Costura visible en pieza cilíndrica | `seam_slope_type=external` (scarf) o `seam_position=back` / `aligned` | Scarf disimula la costura. `back` la esconde detrás. |
| Figura orgánica con voladizos pequeños | `enable_support=1`, `support_type=tree(auto)` | Menos material, se quita fácil. |
| Voladizo plano grande | `enable_support=1`, `support_type=normal(auto)`, interfaz 3 capas | Superficie inferior mejor. |
| Soporte solo desde la cama | `support_on_build_plate_only=1` | Evita cicatrices en la pieza. |
| Soporte cuesta de quitar | `support_top_z_distance=0.24–0.28`, `support_object_xy_distance=0.5` | Más separación. |
| ABS/ASA en A1 | `draft_shield=enabled`, `brim_width=8`, `close_fan_the_first_x_layers=3`, relleno ≤ 20 % | Marco abierto: warping. |
| Piezas pequeñas (< 15 mm lado) sola | Imprimir 2+ copias, o subir `slow_down_layer_time` no hace falta: el perfil ya ralentiza; cooling | Capa se enfría antes → mejor forma. |
| Superficie tipo "textura" deseada / esconder líneas | `fuzzy_skin=external` | Acabado rugoso, oculta capas. |
| Jarrón/maceta de una pared | `spiral_mode=1`, `wall_loops=1`, `top_shell_layers=0`, `sparse_infill_density=0%` | Modo vaso (sin techo, sin relleno). |
| Multicolor con AMS lite | `flush_into_infill=1`, purga ×0.7 en la UI | Menos desperdicio. |
| Anillos/ringing en esquinas | Perfil "High Quality" o `outer_wall_acceleration=2000`, `outer_wall_speed=100` | Menos inercia en pared exterior. |
| Cotas externas exactas | `precise_outer_wall=1` (Bambu 2.x) | Mejora precisión de la pared exterior. |
| Capas finas y techo con huecos | `top_shell_layers` hasta ≥ 0.8–1.0 mm de grosor total | Suficiente cierre superior. |

## 4. Enumerados válidos (texto exacto)
- `support_type`: `tree(auto)`, `normal(auto)`, `tree(manual)`, `normal(manual)`
- `sparse_infill_pattern`: `grid`, `gyroid`, `cubic`, `adaptivecubic`, `honeycomb`, `3dhoneycomb`, `lightning`, `line`, `zig-zag`, `crosshatch`, `tri-hexagon`, `supportcubic`, `concentric`
- `top_surface_pattern` / `bottom_surface_pattern`: `monotonic`, `monotonicline`, `concentric`, `zig-zag`, `alignedrectilinear`, `hilbertcurve`, `archimedeanchords`, `octagramspiral`
- `seam_position`: `aligned`, `nearest`, `back`, `random`
- `seam_slope_type`: `none`, `external`, `all`
- `wall_generator`: `classic`, `arachne`
- `ironing_type`: `no ironing`, `top`, `topmost`, `solid`
- `brim_type`: `auto_brim`, `outer_only`, `inner_only`, `outer_and_inner`, `brim_ears`, `no_brim`
- `print_sequence`: `by layer`, `by object`
- `fuzzy_skin`: `none`, `external`, `all`, `allwalls`
- `draft_shield`: `disabled`, `enabled`
- Placa (`--plate`): `textured`, `smooth`, `cool`, `supertack`, `engineering`

## 5. Solución de problemas (para la sección "si falla…")
| Síntoma | Causa típica | Arreglo |
|---|---|---|
| No pega / se despega | Placa sucia (grasa de dedos), placa ≠ slicer, huella pequeña | Agua caliente + jabón; confirmar placa; brim; SuperTack |
| Warping esquinas | Contracción (ABS/ASA/PETG grande), corrientes | Brim, sin fan inicial, draft shield, cama +5 °C, redondear esquinas |
| Pata de elefante | Cama caliente, primera capa aplastada | `elefant_foot_compensation` 0.15–0.2; cama −5 °C |
| Cuerdas | Humedad, temp alta (PETG/TPU) | Secar; −5 °C; retracción del perfil |
| Voladizos caídos | Poco fan, ángulo excesivo | Soporte, bajar `support_threshold_angle`, reorientar |
| Capas separadas / grietas | Temp baja, fan alto, ABS en marco abierto | +5–10 °C, menos fan, capa más gruesa, draft shield |
| Superficie superior con huecos | Pocas capas superiores, subextrusión | +1–2 `top_shell_layers`, calibrar flow, secar |
| Subextrusión a alta velocidad | Caudal > `filament_max_volumetric_speed` real | Bajar vol. máx en filamento; perfil del filamento correcto |
| Agujeros pequeños | Encogimiento FDM | `xy_hole_compensation` 0.1 o circle compensation |
| Tambaleo / ondas en piezas altas | Bed slinger | Brim, height slowdown, Silent, girar 45° |
| Soporte imposible de quitar | Z distance = 0 sin interfaz distinta | `support_top_z_distance` 0.2–0.28 |
| Atasco con TPU | Demasiado rápido, AMS lite | Bobina externa, ≤ 3 mm³/s, secar |
