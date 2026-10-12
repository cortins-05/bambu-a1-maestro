# Orientación, soportes y lectura de la geometría

Índice: 1. Cómo decidir la orientación · 2. Resistencia (anisotropía) · 3. Voladizos y puentes · 4. Soportes en Bambu Studio · 5. Agujeros, roscas y tolerancias · 6. Piezas altas en bed slinger · 7. Varias piezas en una placa · 8. Qué buscar al mirar los renders

---

## 1. Cómo decidir la orientación (orden de prioridad)

El `score` de `analyze_models.py` solo mira soporte/altura/contacto/esbeltez. Tú decides con este orden, **justificándolo**:

1. **Función / carga** — si la pieza trabaja (clip, soporte, gancho, bisagra, brazo), la carga principal debe ir **a lo largo de las capas**, nunca separándolas (§2). Esto manda sobre la estética y el tiempo.
2. **Precisión de lo que encaja** — agujeros que deben ser redondos y exactos → eje del agujero **vertical (Z)**. Caras que apoyan contra otra pieza → mejor sobre la cama o arriba (planas y exactas).
3. **Caras visibles** — la cara estética no debe llevar soportes (cicatrices). La cara sobre la cama sale con la textura de la placa (Textured PEI = granulada; Smooth = brillo espejo).
4. **Soportes** — minimizar volumen y, sobre todo, soportes en sitios **inaccesibles** (dentro de cavidades, bajo puentes internos).
5. **Adhesión / estabilidad** — cara plana más grande abajo; esbeltez (alto / lado menor huella) > 3 ya pide brim, > 5 pide replantear o ralentizar.
6. **Tiempo** — menos altura = menos capas = menos tiempo (en general).

Trucos:
- Girar **45° sobre Z** una pieza larga reduce el latigazo en Y y a veces cabe en diagonal.
- Inclinar **30–45°** a veces elimina soportes (voladizos pasan a ≤45°) y mejora resistencia (CNC Kitchen: piezas a 45° ~30 % más resistentes que de pie).
- Si ninguna orientación es buena: **partir la pieza** (Bambu Studio: Cut tool con conectores/espigas) y pegar. Proponlo cuando ahorra mucho soporte o mejora mucho la resistencia.
- Una cara plana ligeramente curva o chaflanada abajo = mala adhesión → proponer "Place on face" en Bambu o añadir brim.

## 2. Resistencia (anisotropía FDM)
- En **Z** (entre capas) la resistencia es ~**30–50 %** de la de XY. Una pieza cargada separando capas puede ser 3–5× más débil.
- La resistencia viene sobre todo de **paredes** (perímetros) y capas superior/inferior, no del relleno. Para piezas funcionales: más paredes antes que más relleno.
  - Funcional ligera: 3 paredes, 15–20 % relleno.
  - Funcional media: 4 paredes, 20–30 % gyroid/cubic.
  - Crítica: 5–6 paredes (perfil "0.20mm Strength" = 6 paredes, 25 %), capas superiores/inferiores 5–6.
  - Rellenos por uso: `grid` (rápido, defecto), `gyroid` (isótropo, bueno en flex y TPU), `cubic`/`adaptivecubic` (bueno 3D, sin choques de boquilla), `lightning` (solo sostiene techos; decorativo), `honeycomb` (lento).
- Capa más gruesa (0.24–0.28) = mejor unión entre capas y más rápido; capa fina = mejor detalle pero no más fuerte.
- Temperatura algo alta y menos fan → mejor unión entre capas (para piezas mecánicas en PETG/ABS).
- Agujeros para tornillos: 3–4 paredes alrededor para que no revienten.

## 3. Voladizos y puentes
- Regla 45°: hasta 45° desde la vertical se imprime sin soporte (con buen fan hasta ~55–60° en PLA). El perfil A1 genera soporte auto cuando la superficie queda por debajo de `support_threshold_angle` (desde la horizontal): 30° en 0.20 mm, 15–25° en capas finas, 35–40° en capas gruesas.
- Voladizos redondeados en la base (curvas que empiezan en la cama) son voladizos "rasantes": los primeros 1–2 mm salen algo feos. Un pequeño chaflán de 45° en la base del modelo evita esto (sugerirlo si el usuario diseña).
- Puentes: PLA hasta ~50 mm razonable (más → comba), PETG ~30 mm, ABS ~30 mm. Hasta 10 mm prácticamente siempre bien. El perfil ya ralentiza (`bridge_speed`=50) y usa ventilador de voladizo.
- Techos planos internos grandes → Bambu ya refuerza (`internal_bridge_support_thickness`).
- Voladizos "flotantes" (islas que empiezan en el aire) **siempre** necesitan soporte, aunque sean pequeñas.

## 4. Soportes en Bambu Studio
| Tipo (`support_type`) | Cuándo |
|---|---|
| `tree(auto)` (defecto A1) | Formas orgánicas, figuras, voladizos pequeños dispersos. Menos material, fácil de quitar, menos marcas. |
| `normal(auto)` | Grandes voladizos planos (baldas, techos): mejor superficie bajo el voladizo. |
| `tree(manual)` / `normal(manual)` | Solo donde el usuario pinte soportes ("Support painting") o con enforcers. Ideal para evitar soportes en la cara estética. |
- `enable_support=1` activa. `support_on_build_plate_only=1` evita soportes que arrancan sobre la pieza (cicatrices en caras superiores) — útil cuando los voladizos problemáticos dan a la cama.
- Despegue fácil: `support_top_z_distance` = altura de capa (defecto); subir a 0.24–0.28 si cuesta quitar; interfaz 2–3 capas (`support_interface_top_layers`). `support_object_xy_distance` 0.35 (subir a 0.5 si se funde con paredes verticales).
- Superficie bajo soporte muy limpia: material de interfaz distinto (PLA↔PETG o "Support for PLA/PETG") con `support_top_z_distance=0`.
- Bloqueadores (blockers) en agujeros horizontales pequeños (<8 mm): se imprimen bien sin soporte, el interior del soporte cuesta de sacar.
- `support_threshold_angle`: bajar (ej. 20–25°) si quieres menos soporte y confías en el fan; subir si ves voladizos feos en la validación.

## 5. Agujeros, roscas y tolerancias (A1 bien calibrada, PLA, boquilla 0.4)
- Agujeros verticales salen **~0.1–0.2 mm más pequeños**. Opciones: `xy_hole_compensation` = 0.05–0.15 (agranda todos los agujeros), o `enable_circle_compensation=1` (auto-compensación de círculos de Bambu). Elegir UNA.
- Contornos exteriores sobredimensionados → `xy_contour_compensation` negativo (-0.05). Raro necesitarlo.
- Pata de elefante (primera capa ensanchada): el perfil ya compensa 0.075 mm; para piezas que encajan por la base subir `elefant_foot_compensation` a 0.15–0.2. Con cama más fría (SuperTack) hay menos.
- Holguras de diseño recomendadas (por lado): ajuste a presión 0.05–0.1 mm, deslizante 0.2–0.3 mm, holgado 0.4 mm, print-in-place móviles ≥ 0.3–0.4 mm en XY y ≥ 1 capa en Z. PETG +0.05 mm.
- Agujeros horizontales: salen ovalados arriba (techo en voladizo) → forma lágrima (teardrop) si se diseña; si es de tornillo, taladrar/repasar después o poner eje vertical.
- Roscas: imprimir con eje vertical, capa 0.12–0.16, M6 o mayor realistas; menores → insertos térmicos (agujero según fabricante del inserto, 3–4 paredes).
- Texto/relieve: altura/profundidad ≥ 0.4–0.6 mm y trazo ≥ 0.8 mm; texto en caras verticales se lee mejor con capa fina; texto en la cara superior → `ironing_type=top` lo empeora si está hundido, mejor sin planchado.

## 6. Piezas altas y esbeltas en bed slinger (A1)
Esbeltez = altura / lado menor de la huella (lo da el análisis).
- 2–3: brim 5 mm (`brim_type=outer_only`, `brim_width=5`).
- 3–5: brim 8 mm + `enable_height_slowdown=1` (desde ~50 % de altura) o modo Silent, eje largo de la huella en Y si es posible, acelerar menos (`default_acceleration` 3000–4000).
- \> 5: replantear orientación, añadir "orejas"/costillas temporales, imprimir varias piezas juntas unidas por un puente de sacrificio, o partir la pieza.
- Filamento flexible + pieza alta = combinación de riesgo máximo.

## 7. Varias piezas en una placa
- `print_sequence=by layer` (defecto): todas a la vez, un fallo arruina todo, pero soporta cualquier altura.
- `by object`: una detrás de otra; limitado a piezas ≤ 25 mm de altura (salvo la última) y separación del radio del cabezal (57 mm). Ventaja: un fallo no arruina las demás, menos viajes y hilos entre piezas.
- Piezas iguales: distribuir en el centro de la cama (mejor planitud), separación ≥ 5–10 mm.
- Piezas muy pequeñas solas: tiempo mínimo de capa hace que la boquilla espere/ralentice → imprimir varias copias juntas mejora el enfriamiento y la calidad.

## 8. Qué buscar al mirar los renders
Mira la hoja de vistas (`*_vistas.png`) y los mapas de voladizo (`*_orientN_voladizos.png`, rojo = voladizo) y anota:
- **Tipo de pieza**: carcasa, soporte/bracket, engranaje, clip, figura, caja con tapa, adaptador, pieza con orejetas de tornillo…
- **Rasgos que condicionan**: agujeros (y su eje), ranuras, pestañas en voladizo, clips flexibles (cargados a flexión → capas paralelas a la flexión), paredes finas, texto, roscas, superficies curvas grandes, cavidades cerradas.
- **Caras planas grandes** → candidatas a apoyar en cama.
- **Rojo en caras visibles** → soporte con cicatriz; valorar otra orientación o soporte pintado manual.
- **Rojo en el interior de cavidades** → soporte inaccesible: evitar.
- Multi-cuerpo en un archivo → ¿se imprimen juntos o separarlos?
- La cara inferior del render "Abajo (-Z)" es la que tocará la cama en la orientación original.
