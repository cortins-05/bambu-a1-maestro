# Valores OFICIALES de los perfiles Bambu Studio para A1 (boquilla 0.4)

Extraído automáticamente de `resources/profiles/BBL` de Bambu Studio instalado (sep-2026). Son los valores por defecto que el slicer carga. 0 en una placa = placa no recomendada para ese material.

Regenerar / consultar cualquier valor: `python scripts/bambu_slice.py --show filament "<nombre>" --keys k1,k2`

## Máquina: Bambu Lab A1 0.4 nozzle
- `printable_area` = ['0x0', '256x0', '256x256', '0x256']
- `printable_height` = 256
- `nozzle_type` = ['stainless_steel']
- `nozzle_volume` = ['92']
- `machine_max_speed_x` = ['500', '200']
- `machine_max_speed_y` = ['500', '200']
- `machine_max_acceleration_x` = ['12000', '12000']
- `machine_max_acceleration_extruding` = ['12000', '12000']
- `retraction_length` = ['0.8']
- `retraction_speed` = ['30']
- `z_hop` = ['0.4']
- `z_hop_types` = ['Auto Lift']
- `extruder_clearance_height_to_rod` = 25
- `extruder_clearance_radius` = 57
- `extruder_clearance_max_radius` = 73
- `default_print_profile` = 0.20mm Standard @BBL A1
- `default_filament_profile` = ['Bambu PLA Basic @BBL A1']

## Perfiles de proceso A1 0.4

| clave | 0.08mm Extra Fine | 0.08mm High Quality | 0.12mm Fine | 0.12mm High Quality | 0.16mm High Quality | 0.16mm Optimal | 0.20mm Standard | 0.20mm Strength | 0.24mm Draft | 0.28mm Extra Draft |
|---|---|---|---|---|---|---|---|---|---|---|
| layer_height | 0.08 | 0.08 | 0.12 | 0.12 | 0.16 | 0.16 | 0.2 | 0.2 | 0.24 | 0.28 |
| initial_layer_print_height | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 | 0.2 |
| wall_loops | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 6 | 2 | 2 |
| top_shell_layers | 9 | 9 | 5 | 5 | 6 | 6 | 5 | 5 | 4 | 4 |
| bottom_shell_layers | 7 | 7 | 5 | 5 | 4 | 4 | 3 | 3 | 3 | 3 |
| top_shell_thickness | 0.8 | 0.8 | 0.6 | 0.6 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| sparse_infill_density | 15% | 15% | 15% | 15% | 15% | 15% | 15% | 25% | 15% | 15% |
| sparse_infill_pattern | grid | gyroid | grid | gyroid | gyroid | grid | grid | grid | grid | grid |
| outer_wall_speed | 200 | 60 | 200 | 60 | 60 | 200 | 200 | 60 | 200 | 200 |
| inner_wall_speed | 350 | 120 | 350 | 150 | 150 | 300 | 300 | 300 | 230 | 200 |
| sparse_infill_speed | 450 | 150 | 430 | 180 | 200 | 330 | 270 | 270 | 230 | 200 |
| top_surface_speed | 200 | 150 | 200 | 150 | 150 | 200 | 200 | 200 | 200 | 200 |
| default_acceleration | 6000 | 4000 | 6000 | 4000 | 4000 | 6000 | 6000 | 6000 | 6000 | 6000 |
| outer_wall_acceleration | 5000 | 2000 | 5000 | 2000 | 2000 | 5000 | 5000 | 5000 | 5000 | 5000 |
| top_surface_acceleration | 2000 | 2000 | 2000 | 2000 | 2000 | 2000 | 2000 | 2000 | 2000 | 2000 |
| elefant_foot_compensation | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 | 0.075 |
| support_type | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) | tree(auto) |
| support_threshold_angle | 15 | 15 | 20 | 20 | 25 | 25 | 30 | 30 | 35 | 40 |
| support_top_z_distance | 0.08 | 0.08 | 0.12 | 0.12 | 0.16 | 0.16 | 0.2 | 0.2 | 0.2 | 0.2 |
| seam_position | aligned | aligned | aligned | aligned | aligned | aligned | aligned | aligned | aligned | aligned |
| wall_generator | classic | classic | classic | classic | classic | classic | classic | classic | classic | classic |
| brim_width | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| brim_type | - | - | - | - | - | - | - | - | - | - |
| ironing_type | no ironing | no ironing | no ironing | no ironing | no ironing | no ironing | no ironing | no ironing | no ironing | no ironing |
| enable_prime_tower | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Otras claves comunes (0.20mm Standard):
`line_width`=0.42, `outer_wall_line_width`=0.42, `initial_layer_line_width`=0.5, `initial_layer_speed`=50, `initial_layer_acceleration`=500, `travel_speed`=700, `bridge_speed`=50, `bridge_flow`=1, `gap_infill_speed`=250, `small_perimeter_speed`=50%, `overhang_2_4_speed`=50, `overhang_3_4_speed`=30, `overhang_4_4_speed`=10, `support_interface_top_layers`=2, `support_object_xy_distance`=0.35, `tree_support_branch_angle`=45, `infill_wall_overlap`=15%, `only_one_wall_top`=1, `detect_thin_wall`=0, `xy_hole_compensation`=0, `xy_contour_compensation`=0, `enable_circle_compensation`=0, `resolution`=0.012, `enable_arc_fitting`=1, `skirt_loops`=0, `prime_tower_width`=35, `print_sequence`=by layer, `reduce_infill_retraction_mode`=Auto, `wall_infill_order`=inner wall/outer wall/infill, `top_surface_pattern`=monotonicline, `bottom_surface_pattern`=monotonic, `enable_overhang_speed`=1

## Filamentos A1 0.4 (Bambu + Generic)

| Filamento | T boquilla | T 1ª capa | rango | Textured | Smooth PEI | Cool | SuperTack | Eng | Fan min-max % | Fan voladizo | Sin fan 1ª N capas | t capa min s | Vol. máx mm³/s | Flow | Retracción | Tg °C | Densidad |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bambu ABS | 270 | 260 | 240-280 | 100 | 100 | 0 | 0 | 90 | 10-20 | 80 | 3 | 12 | 16 | 0.95 | 0.4 | 100 | 1.04 |
| Bambu ABS-GF | 270 | 260 | 240-280 | 90 | 90 | 0 | 0 | 90 | 10-30 | 30 | 3 | 4 | 12 | 0.95 | - | 100 | 1.08 |
| Bambu ASA 0.4 nozzle | 270 | 270 | 240-280 | 100 | 100 | 0 | 0 | 100 | 10-35 | 80 | 3 | 12 | 18 | 0.95 | - | 100 | 1.05 |
| Bambu ASA-Aero | 270 | 270 | 240-280 | 90 | 90 | 0 | 0 | 90 | 30-50 | 50 | 3 | 5 | 12 | 0.52 | 1.5 | 100 | 0.99 |
| Bambu ASA-CF | 275 | 275 | 250-280 | 100 | 100 | 0 | 0 | 100 | 10-25 | 80 | 3 | 12 | 18 | 0.9 | - | 108 | 1.02 |
| Bambu PA-CF | 290 | 290 | 260-300 | 100 | 100 | 0 | 0 | 100 | 10-30 | 40 | 3 | 2 | 8 | 0.96 | - | 170 | 1.09 |
| Bambu PA6-CF | 275 | 275 | 260-300 | 100 | 100 | 0 | 0 | 100 | 10-30 | 40 | 3 | 2 | 8 | 0.96 | - | 170 | 1.10 |
| Bambu PA6-GF | 265 | 265 | 260-300 | 100 | 100 | 0 | 0 | 100 | 10-30 | 40 | 3 | 2 | 10.5 | 0.96 | - | 180 | 1.14 |
| Bambu PAHT-CF | 290 | 290 | 260-300 | 100 | 100 | 0 | 0 | 100 | 10-30 | 40 | 3 | 2 | 8 | 0.96 | - | 180 | 1.06 |
| Bambu PC | 280 | 270 | 260-290 | 100 | 100 | 0 | 0 | 100 | 10-20 | 60 | 3 | 12 | 18 | 0.94 | - | 120 | 1.185 |
| Bambu PC FR | 280 | 270 | 260-290 | 100 | 100 | 0 | 0 | 100 | 10-20 | 60 | 3 | 12 | 18 | 0.94 | - | 120 | 1.19 |
| Bambu PET-CF | 270 | 270 | 260-290 | 100 | 100 | 0 | 80 | 80 | 1-80 | 75 | 3 | 1 | 5 | 0.9555 | - | 185 | 1.29 |
| Bambu PETG Basic | 245 | 245 | 230-270 | 70 | 70 | 0 | 70 | 70 | 30-50 | 50 | 3 | 12 | 13 | 0.94 | 0.4 | 60 | 1.25 |
| Bambu PETG HF | 240 | 230 | 230-270 | 70 | 70 | 0 | 70 | 70 | 30-50 | 100 | 3 | 7 | 18 | 0.94 | - | 70 | 1.28 |
| Bambu PETG Matte | 235 | 235 | 230-270 | 70 | 70 | 0 | 70 | 70 | 30-50 | 50 | 3 | 12 | 13 | 0.94 | 0.8 | 70 | 1.37 |
| Bambu PETG Translucent | 245 | 250 | 230-270 | 70 | 70 | 0 | 70 | 70 | 10-30 | 90 | 3 | 8 | 6 | 0.95 | 0.3 | 70 | 1.25 |
| Bambu PETG-CF 0.4 nozzle | 255 | 255 | 240-270 | 70 | 70 | 0 | 70 | 70 | 5-40 | 100 | 3 | 6 | 9 | 0.95 | - | 70 | 1.25 |
| Bambu PLA Aero | 220 | 220 | 210-260 | 65 | 65 | 35 | 0 | 0 | 60-80 | 100 | 1 | 8 | 6 | 0.6 | - | 45 | 1.21 |
| Bambu PLA Basic | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 21 | 0.98 | - | 45 | 1.26 |
| Bambu PLA Dynamic | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 21 | 0.98 | - | 45 | 1.26 |
| Bambu PLA Galaxy | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 21 | 0.98 | - | 45 | 1.19 |
| Bambu PLA Glow | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 50-100 | 100 | 1 | 8 | 18 | 0.98 | - | 45 | 1.26 |
| Bambu PLA Lite | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 16 | 0.98 | - | 45 | 1.40 |
| Bambu PLA Marble | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 12 | 0.98 | - | 45 | 1.22 |
| Bambu PLA Matte | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 22 | 0.98 | - | 45 | 1.32 |
| Bambu PLA Metal | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 21 | 0.98 | - | 45 | 1.25 |
| Bambu PLA Pure | 220 | 220 | 190-220 | 65 | 65 | 35 | 45 | 0 | 60-100 | 100 | 1 | 10 | 12 | 0.98 | 0.4 | 45 | 1.24 |
| Bambu PLA Silk | 230 | 230 | 190-240 | 65 | 65 | 35 | 0 | 0 | 60-80 | 100 | 1 | 8 | 12 | 0.98 | - | 45 | 1.32 |
| Bambu PLA Silk+ | 230 | 230 | 190-240 | 65 | 65 | 35 | 35 | 0 | 60-80 | 100 | 1 | 8 | 12 | 0.98 | - | 45 | 1.27 |
| Bambu PLA Sparkle | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 12 | 0.98 | - | 45 | 1.26 |
| Bambu PLA Tough | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 21 | 0.98 | - | 45 | 1.26 |
| Bambu PLA Tough+ | 245 | 245 | 220-250 | 65 | 65 | 35 | 45 | 0 | 90-100 | 100 | 1 | 8 | 18 | 0.98 | - | 45 | 1.21 |
| Bambu PLA Translucent | 220 | 220 | 200-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 8 | 12 | 0.98 | - | 45 | 1.22 |
| Bambu PLA Wood | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 18 | 0.98 | - | 45 | 1.21 |
| Bambu PLA-CF | 230 | 230 | 210-250 | 65 | 65 | 45 | 50 | 0 | 60-80 | 100 | 1 | 6 | 15 | 0.98 | - | 45 | 1.22 |
| Bambu PVA | 240 | 240 | 210-250 | 65 | 65 | 45 | 35 | 0 | 60-80 | 100 | 1 | 8 | 6 | 1 | - | 45 | 1.27 |
| Bambu Support For PA/PET | 280 | 280 | 260-300 | 100 | 100 | 0 | 0 | 100 | 0-60 | 30 | 3 | 6 | 8 | 1 | - | 108 | 1.22 |
| Bambu Support For PLA | 220 | 220 | 190-240 | 65 | 65 | 40 | 45 | 0 | 60-80 | 100 | 1 | 8 | 12 | 1 | - | 45 | 1.30 |
| Bambu Support For PLA/PETG | 210 | 210 | 190-240 | 65 | 65 | 35 | 45 | 65 | 20-30 | 100 | 1 | 8 | 6 | 1 | - | 45 | 1.19 |
| Bambu Support G | 280 | 280 | 260-300 | 100 | 100 | 0 | 0 | 100 | 0-60 | 30 | 3 | 6 | 8 | 1 | - | 108 | 1.22 |
| Bambu Support W | 220 | 220 | 190-240 | 65 | 65 | 40 | 45 | 0 | 60-80 | 100 | 1 | 8 | 12 | 1 | - | 45 | 1.30 |
| Bambu Support for ABS | 270 | 260 | 240-270 | 90 | 90 | 0 | 0 | 90 | 10-30 | 80 | 3 | 12 | 6 | 0.95 | - | 90 | 1.16 |
| Bambu TPU 90A | 225 | 225 | 200-250 | 45 | 45 | 30 | 0 | 30 | 100-100 | 100 | 1 | 14 | 2.8 | 1 | 0.4 | 30 | 1.22 |
| Bambu TPU 95A | 230 | 230 | 200-250 | 45 | 45 | 30 | 0 | 30 | 100-100 | 100 | 1 | 8 | 3.6 | 1 | 0.4 | 30 | 1.22 |
| Bambu TPU 95A HF | 230 | 230 | 200-250 | 45 | 45 | 30 | 0 | 30 | 100-100 | 100 | 1 | 8 | 12 | 1 | 0.8 | 30 | 1.22 |
| Bambu TPU for AMS | 230 | 230 | 220-240 | 35 | 35 | 30 | 0 | 30 | 20-40 | 100 | 1 | 10 | 18 | 0.97 | 0.4 | 30 | 1.26 |
| Generic ABS | 270 | 260 | 240-280 | 100 | 100 | 0 | 0 | 90 | 10-20 | 80 | 3 | 3 | 15 | 0.95 | 0.4 | 100 | 1.04 |
| Generic ASA | 260 | 260 | 240-280 | 100 | 100 | 0 | 0 | 100 | 10-80 | 80 | 3 | 3 | 12 | 0.95 | - | 100 | 1.04 |
| Generic BVOH | 220 | 220 | 190-240 | 55 | 55 | 40 | 0 | 0 | 100-100 | 100 | 1 | 8 | 8 | 1 | - | 45 | 1.13 |
| Generic EVA | 210 | 210 | 175-220 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 12 | 1 | - | 70 | 0.94 |
| Generic HIPS | 240 | 240 | 220-270 | 70 | 70 | 0 | 0 | 70 | 0-60 | 80 | 3 | 6 | 8 | 1 | - | 100 | 1.06 |
| Generic PA | 260 | 260 | 240-280 | 100 | 100 | 0 | 0 | 100 | 40-85 | 95 | 3 | 8 | 12 | 1 | - | 108 | 1.04 |
| Generic PA-CF | 290 | 290 | 260-300 | 100 | 100 | 0 | 0 | 100 | 10-30 | 40 | 3 | 2 | 8 | 1 | - | 108 | 1.04 |
| Generic PC | 280 | 270 | 260-290 | 100 | 100 | 0 | 0 | 100 | 10-20 | 60 | 3 | 2 | 16 | 0.94 | - | 120 | 1.04 |
| Generic PCTG | 255 | 255 | 240-270 | 70 | 70 | 0 | 0 | 70 | 10-40 | 90 | 3 | 12 | 6 | 0.95 | - | 90 | 1.29 |
| Generic PE | 210 | 210 | 175-220 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 8 | 1 | - | 70 | 0.95 |
| Generic PE-CF | 210 | 210 | 175-220 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 6 | 1 | - | 70 | 0.95 |
| Generic PETG | 255 | 255 | 220-270 | 80 | 80 | 0 | 70 | 70 | 40-90 | 90 | 3 | 12 | 8 | 0.95 | - | 70 | 1.27 |
| Generic PETG HF | 220 | 220 | 220-270 | 70 | 70 | 0 | 70 | 70 | 20-40 | 90 | 3 | 25 | 16 | 0.95 | 0.4 | 70 | 1.28 |
| Generic PETG-CF | 255 | 255 | 240-270 | 70 | 70 | 0 | 70 | 70 | 5-40 | 100 | 3 | 6 | 8 | 0.95 | - | 70 | 1.25 |
| Generic PHA | 220 | 220 | 190-240 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 6 | 1 | - | 120 | 1.24 |
| Generic PLA | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 8 | 12 | 0.98 | - | 45 | 1.24 |
| Generic PLA High Speed | 220 | 220 | 190-240 | 65 | 65 | 35 | 45 | 0 | 60-80 | 100 | 1 | 6 | 18 | 0.98 | - | 45 | 1.24 |
| Generic PLA Silk | 220 | 220 | 190-240 | 55 | 55 | 35 | 35 | 0 | 60-80 | 100 | 1 | 8 | 7.5 | 0.98 | 0.5 | 45 | 1.24 |
| Generic PLA-CF | 220 | 220 | 190-240 | 65 | 65 | 45 | 50 | 0 | 60-80 | 100 | 1 | 8 | 12 | 0.95 | - | 45 | 1.24 |
| Generic PP | 235 | 235 | 220-250 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 12 | 1 | - | 110 | 0.93 |
| Generic PP-CF | 235 | 235 | 220-250 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 6 | 1 | - | 110 | 1.01 |
| Generic PP-GF | 235 | 235 | 220-250 | 55 | 55 | 35 | 0 | 0 | 100-100 | 100 | 1 | 4 | 6 | 1 | - | 110 | 1.05 |
| Generic PVA | 220 | 220 | 190-240 | 65 | 65 | 45 | 35 | 0 | 60-80 | 100 | 1 | 8 | 16 | 0.95 | - | 45 | 1.24 |
| Generic TPU | 240 | 240 | 200-250 | 45 | 45 | 30 | 0 | 30 | 100-100 | 100 | 1 | 8 | 3.2 | 1 | 0.4 | 30 | 1.24 |
| Generic TPU for AMS | 230 | 230 | 200-250 | 35 | 35 | 30 | 0 | 30 | 10-50 | 100 | 1 | 10 | 10.5 | 1 | 0.8 | 30 | 1.26 |
