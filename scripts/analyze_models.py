#!/usr/bin/env python3
"""
analyze_models.py — Análisis geométrico + renders de modelos 3D para imprimir en Bambu Lab A1.

Uso:
    python analyze_models.py <ruta_archivo_o_carpeta> [--out DIR] [--threshold 45] [--top 3]

Qué hace por cada modelo (.stl .3mf .obj .ply .glb .gltf .off .step/.stp*):  (*STEP: pip install cascadio)
  1. Carga, valida (estanco, normales, cuerpos sueltos, unidades sospechosas).
  2. Mide: tamaño, volumen, área, gramos estimados por material, genus (agujeros pasantes).
  3. Prueba orientaciones candidatas (poses estables + 6 caras) y para cada una calcula:
     altura, área de contacto con la cama, área de voladizo, volumen estimado de soporte,
     riesgo de vuelco (esbeltez) y si cabe en 256x256x256.
  4. Muestrea grosor de pared (rayos hacia dentro) → detecta paredes finas.
  5. Genera PNG: hoja de vistas (6 ortogonales + iso) y mapa de voladizos de las mejores orientaciones.
  6. Exporta STL ya orientado de cada orientación top (para laminar con --orient 0).

Salida: <out>/report.json, <out>/report.md y PNG/STL. Lee report.md primero, luego mira los PNG.
Dependencias: pip install trimesh numpy matplotlib scipy rtree networkx
"""
import argparse
import hashlib
import json
import math
import os
import sys
import warnings

warnings.filterwarnings("ignore")

try:  # consolas Windows cp1252 no soportan emojis/acentos
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    import numpy as np
    import trimesh
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError as e:  # pragma: no cover
    print(f"[ERROR] Falta dependencia: {e}\n  Instala: pip install trimesh numpy matplotlib scipy rtree networkx")
    sys.exit(2)

BED = (256.0, 256.0, 256.0)          # A1 volumen imprimible mm
EXTS = (".stl", ".3mf", ".obj", ".ply", ".glb", ".gltf", ".off", ".step", ".stp")  # STEP requiere: pip install cascadio
DENSITY = {"PLA": 1.26, "PETG": 1.27, "ABS": 1.04, "ASA": 1.05, "TPU": 1.22, "PC": 1.19, "PA-CF": 1.12}
MAX_RENDER_FACES = 60000


# ---------------------------------------------------------------- utilidades
def load_mesh(path):
    try:
        obj = trimesh.load(path, force=None)
    except Exception as e:
        if path.lower().endswith((".step", ".stp")):
            raise RuntimeError(f"No se pudo leer STEP ({e}). Instala: pip install cascadio  — o exporta a STL/3MF.")
        raise
    if isinstance(obj, trimesh.Scene):
        geoms = [g for g in obj.dump() if isinstance(g, trimesh.Trimesh)] if hasattr(obj, "dump") else list(obj.geometry.values())
        if not geoms:
            raise ValueError("Escena sin mallas")
        mesh = trimesh.util.concatenate(geoms)
    else:
        mesh = obj
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"Tipo no soportado: {type(mesh)}")
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()
    return mesh


def rot_to_down(normal):
    """Matriz 4x4 que gira el vector `normal` para que apunte a -Z (esa cara queda sobre la cama)."""
    return trimesh.geometry.align_vectors(np.asarray(normal, float), [0, 0, -1])


def place_on_bed(mesh):
    m = mesh.copy()
    b = m.bounds
    m.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    return m


def ray_engine(mesh):
    try:
        return trimesh.ray.ray_triangle.RayMeshIntersector(mesh)
    except Exception:
        return mesh.ray


# ---------------------------------------------------------------- orientación
def evaluate_orientation(mesh, T, thr_deg, ray_budget=4000):
    m = mesh.copy()
    m.apply_transform(T)
    m = place_on_bed(m)
    ext = m.extents
    n = m.face_normals
    areas = m.area_faces
    cent = m.triangles_center
    zmin = 0.0

    on_bed = (cent[:, 2] < zmin + 0.15) & (n[:, 2] < -0.97)
    contact = float(areas[on_bed].sum())

    # voladizo: cara mira hacia abajo más de lo permitido (thr medido desde la vertical: 45° = regla clásica)
    lim = -math.cos(math.radians(90 - thr_deg))  # thr 45 -> -0.707
    over = (n[:, 2] < lim) & (~on_bed) & (cent[:, 2] > 0.3)
    over_area = float(areas[over].sum())

    # volumen de soporte ≈ área proyectada * altura libre bajo la cara (ray-cast hacia abajo)
    sup_vol = 0.0
    idx = np.nonzero(over)[0]
    if len(idx):
        if len(idx) > ray_budget:
            p = areas[idx] / areas[idx].sum()
            pick = np.random.default_rng(0).choice(idx, ray_budget, replace=False, p=p)
            scale = areas[idx].sum() / areas[pick].sum()
        else:
            pick, scale = idx, 1.0
        origins = cent[pick] + n[pick] * 0.01
        dirs = np.tile([0, 0, -1.0], (len(pick), 1))
        heights = origins[:, 2].copy()
        try:
            eng = ray_engine(m)
            locs, ray_i, _ = eng.intersects_location(origins, dirs, multiple_hits=True)
            for r in range(len(pick)):
                hits = locs[ray_i == r]
                if len(hits):
                    hz = hits[:, 2][hits[:, 2] < origins[r, 2] - 0.05]
                    if len(hz):
                        heights[r] = origins[r, 2] - hz.max()
        except Exception:
            pass
        proj = areas[pick] * np.abs(n[pick, 2])
        sup_vol = float((proj * heights).sum() * scale)

    # esbeltez: altura / lado menor de la huella (bbox XY)
    min_xy = max(min(ext[0], ext[1]), 1e-6)
    slender = float(ext[2] / min_xy)
    fits = bool(ext[0] <= BED[0] - 2 and ext[1] <= BED[1] - 2 and ext[2] <= BED[2])
    # coste heurístico (menor = mejor): soporte pesa mucho, altura = tiempo, poco contacto = riesgo
    score = sup_vol / 1000.0 * 3 + ext[2] * 0.05 + (5 if contact < 50 else 0) + max(0, slender - 3) * 2 + (0 if fits else 1000)
    return {
        "size_xyz_mm": [round(float(v), 2) for v in ext],
        "height_mm": round(float(ext[2]), 2),
        "bed_contact_mm2": round(contact, 1),
        "overhang_area_mm2": round(over_area, 1),
        "support_volume_est_cm3": round(sup_vol / 1000.0, 2),
        "slenderness_h_over_minxy": round(slender, 2),
        "fits_A1": fits,
        "score": round(float(score), 3),
    }, m, over


def candidate_transforms(mesh, max_stable=8):
    cands = []
    try:
        Ts, probs = trimesh.poses.compute_stable_poses(mesh, n_samples=1, threshold=0.0)
        for T, p in list(zip(Ts, probs))[:max_stable]:
            cands.append((f"estable p={p:.2f}", T))
    except Exception:
        pass
    faces = {"-Z (tal cual)": [0, 0, -1], "+Z": [0, 0, 1], "-X": [-1, 0, 0], "+X": [1, 0, 0], "-Y": [0, -1, 0], "+Y": [0, 1, 0]}
    for name, v in faces.items():
        cands.append((f"cara {name} abajo", rot_to_down(v)))
    return cands


def dedupe(results):
    out = []
    for r in sorted(results, key=lambda r: r["metrics"]["score"]):
        key = tuple(round(x, 0) for x in r["metrics"]["size_xyz_mm"]) + (round(r["metrics"]["support_volume_est_cm3"], 0),)
        if all(k["_key"] != key for k in out):
            r["_key"] = key
            out.append(r)
    return out


# ---------------------------------------------------------------- grosor de pared
def wall_thickness(mesh, samples=3000):
    try:
        pts, fidx = trimesh.sample.sample_surface(mesh, samples, seed=1)
    except TypeError:
        pts, fidx = trimesh.sample.sample_surface(mesh, samples)
    n = mesh.face_normals[fidx]
    origins = pts - n * 0.01
    try:
        eng = ray_engine(mesh)
        locs, ray_i, _ = eng.intersects_location(origins, -n, multiple_hits=False)
    except Exception:
        return None
    d = np.full(len(pts), np.nan)
    d[ray_i] = np.linalg.norm(locs - origins[ray_i], axis=1)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return None
    return {
        "p5_mm": round(float(np.percentile(d, 5)), 2),
        "p25_mm": round(float(np.percentile(d, 25)), 2),
        "median_mm": round(float(np.median(d)), 2),
        "frac_below_0.45mm": round(float((d < 0.45).mean()), 3),
        "frac_below_0.8mm": round(float((d < 0.8).mean()), 3),
        "frac_below_1.2mm": round(float((d < 1.2).mean()), 3),
    }


# ---------------------------------------------------------------- render
def _decimate_for_render(mesh):
    if len(mesh.faces) <= MAX_RENDER_FACES:
        return mesh, np.arange(len(mesh.faces))
    try:
        s = mesh.simplify_quadric_decimation(face_count=MAX_RENDER_FACES)
        return s, None
    except Exception:
        idx = np.random.default_rng(0).choice(len(mesh.faces), MAX_RENDER_FACES, replace=False)
        return mesh.submesh([idx], append=True), idx


def _draw(ax, mesh, elev, azim, face_colors=None, title=""):
    tris = mesh.triangles
    n = mesh.face_normals
    # luz direccional desde la cámara aprox.
    e, a = math.radians(elev), math.radians(azim)
    cam = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    light = cam + np.array([0.3, -0.3, 0.6])
    light /= np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
    if face_colors is None:
        base = np.array([0.30, 0.55, 0.85])
        cols = np.clip(base[None, :] * shade[:, None] + 0.05, 0, 1)
    else:
        cols = np.clip(face_colors[:, :3] * shade[:, None], 0, 1)
    pc = Poly3DCollection(tris, facecolors=cols, edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    b = mesh.bounds
    c = b.mean(axis=0)
    r = (b[1] - b[0]).max() / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    try:
        ax.set_box_aspect((1, 1, 1))
        ax.set_proj_type("ortho")
    except Exception:
        pass
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("X", fontsize=7)
    ax.set_ylabel("Y", fontsize=7)
    ax.set_zlabel("Z", fontsize=7)
    ax.tick_params(labelsize=6)
    # en vistas ortogonales ocultar el eje que apunta a cámara (evita números amontonados)
    if abs(elev) == 90:
        ax.set_zticks([]); ax.set_zlabel("")
    elif elev == 0 and azim in (90, -90):
        ax.set_yticks([]); ax.set_ylabel("")
    elif elev == 0 and azim in (0, 180):
        ax.set_xticks([]); ax.set_xlabel("")


VIEWS = [("Frente (-Y)", 0, -90), ("Atrás (+Y)", 0, 90), ("Izq (-X)", 0, 180),
         ("Der (+X)", 0, 0), ("Arriba (+Z)", 90, -90), ("Abajo (-Z)", -90, -90),
         ("Iso", 30, -60), ("Iso trasera-inferior", -30, 120)]


def render_sheet(mesh, path, title):
    m, _ = _decimate_for_render(mesh)
    fig = plt.figure(figsize=(16, 8.5), dpi=90)
    for i, (name, el, az) in enumerate(VIEWS):
        ax = fig.add_subplot(2, 4, i + 1, projection="3d")
        _draw(ax, m, el, az, title=name)
    e = mesh.extents
    fig.suptitle(f"{title}  —  {e[0]:.1f} x {e[1]:.1f} x {e[2]:.1f} mm", fontsize=12)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def render_overhang(m_oriented, over_mask, path, title):
    cols = np.tile([0.55, 0.75, 0.95, 1.0], (len(m_oriented.faces), 1))
    cols[over_mask] = [0.95, 0.15, 0.15, 1.0]
    if len(m_oriented.faces) > MAX_RENDER_FACES:
        idx = np.random.default_rng(0).choice(len(m_oriented.faces), MAX_RENDER_FACES, replace=False)
        sub = m_oriented.submesh([idx], append=True)
        cols = cols[idx]
    else:
        sub = m_oriented
    fig = plt.figure(figsize=(14, 4.8), dpi=90)
    for i, (name, el, az) in enumerate([("Iso", 25, -60), ("Desde abajo", -35, -60), ("Frente", 0, -90), ("Lado", 0, 0)]):
        ax = fig.add_subplot(1, 4, i + 1, projection="3d")
        _draw(ax, sub, el, az, face_colors=cols, title=name)
        # plano de cama
        b = sub.bounds
        xx, yy = np.meshgrid([b[0][0] - 2, b[1][0] + 2], [b[0][1] - 2, b[1][1] + 2])
        ax.plot_surface(xx, yy, np.zeros_like(xx), color=(0.2, 0.2, 0.2), alpha=0.25)
    fig.suptitle(title + "   (rojo = voladizo que pedirá soporte)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- principal
def analyze(path, out, thr, top):
    name = os.path.splitext(os.path.basename(path))[0]
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)
    safe += "_" + hashlib.sha256(os.path.abspath(path).encode("utf-8")).hexdigest()[:12]
    rep = {"file": os.path.abspath(path), "name": name}
    mesh = load_mesh(path)
    ext = mesh.extents
    bodies = mesh.split(only_watertight=False) if len(mesh.faces) < 400000 else [mesh]
    rep["triangles"] = int(len(mesh.faces))
    rep["bodies"] = int(len(bodies))
    rep["watertight"] = bool(mesh.is_watertight)
    rep["winding_consistent"] = bool(mesh.is_winding_consistent)
    rep["size_as_loaded_mm"] = [round(float(v), 2) for v in ext]
    vol = float(abs(mesh.volume)) if mesh.is_watertight else float(abs(mesh.convex_hull.volume))
    rep["volume_cm3"] = round(vol / 1000, 3)
    rep["volume_is_exact"] = bool(mesh.is_watertight)
    rep["surface_area_cm2"] = round(float(mesh.area) / 100, 2)
    try:
        rep["genus_through_holes"] = int(round(1 - mesh.euler_number / 2)) if mesh.is_watertight and len(bodies) == 1 else None
    except Exception:
        rep["genus_through_holes"] = None
    # gramos: sólido 100% y estimado típico (2 paredes/15% ≈ cáscara + relleno)
    shell_cm3 = min(vol, float(mesh.area) * 0.84 + 0) / 1000  # ~2 perímetros de 0.42
    typ_cm3 = shell_cm3 + max(vol / 1000 - shell_cm3, 0) * 0.15
    rep["grams_estimate"] = {k: {"solid_100%": round(vol / 1000 * d, 1), "typical_2walls_15%": round(typ_cm3 * d, 1)} for k, d in DENSITY.items()}

    warn = []
    mx = float(ext.max())
    if mx < 3:
        warn.append("Tamaño < 3 mm: probablemente unidades en metros o pulgadas → escalar (x1000 o x25.4).")
    elif mx < 12:
        warn.append("Pieza muy pequeña (<12 mm): revisar si está en pulgadas (x25.4); detalles finos → 0.12/0.08 mm o boquilla 0.2.")
    if not mesh.is_watertight:
        warn.append("Malla NO estanca (agujeros): Bambu Studio intentará reparar; revisar resultado o reparar antes.")
    if not mesh.is_winding_consistent:
        warn.append("Normales inconsistentes: posibles caras invertidas.")
    if len(bodies) > 1:
        warn.append(f"{len(bodies)} cuerpos separados en el archivo: ¿piezas distintas? (se pueden separar en Bambu Studio 'Split to objects').")
    rep["warnings"] = warn

    wt = wall_thickness(mesh)
    rep["wall_thickness"] = wt
    if wt:
        if wt["frac_below_0.45mm"] > 0.02:
            warn.append(f"{wt['frac_below_0.45mm']*100:.1f}% de superficie con pared < 0.45 mm: NO imprimible con boquilla 0.4 (usar 0.2 o engrosar).")
        if wt["frac_below_0.8mm"] > 0.05:
            warn.append(f"{wt['frac_below_0.8mm']*100:.1f}% con pared < 0.8 mm: activar Arachne y/o 'detect thin wall'.")

    # orientaciones
    results = []
    for label, T in candidate_transforms(mesh):
        try:
            met, m_or, over = evaluate_orientation(mesh, T, thr)
            results.append({"label": label, "T": T, "metrics": met, "_m": m_or, "_over": over})
        except Exception as ex:
            results.append({"label": label, "error": str(ex), "metrics": {"score": 1e9, "size_xyz_mm": [0, 0, 0], "support_volume_est_cm3": 0}})
    results = [r for r in dedupe(results) if "error" not in r]
    rep["orientations"] = []
    for k, r in enumerate(results[: max(top, 1) + 3]):
        entry = {"rank": k + 1, "label": r["label"], **r["metrics"],
                 "transform_4x4": [[round(float(x), 5) for x in row] for row in r["T"]]}
        if k < top:
            png = os.path.join(out, f"{safe}_orient{k+1}_voladizos.png")
            render_overhang(r["_m"], r["_over"], png,
                            f"{name} · orientación #{k+1} ({r['label']}) · h={r['metrics']['height_mm']} mm · soporte≈{r['metrics']['support_volume_est_cm3']} cm³")
            stl = os.path.join(out, f"{safe}_orient{k+1}.stl")
            r["_m"].export(stl)
            entry["png"] = os.path.basename(png)
            entry["oriented_stl"] = os.path.abspath(stl)
        rep["orientations"].append(entry)
    if results and not results[0]["metrics"]["fits_A1"]:
        warn.append("No cabe en 256x256x256 en ninguna orientación probada: escalar, partir la pieza o girar en diagonal (diagonal cama ≈ 360 mm).")

    sheet = os.path.join(out, f"{safe}_vistas.png")
    render_sheet(place_on_bed(mesh), sheet, f"{name} (orientación original)")
    rep["views_png"] = os.path.basename(sheet)
    return rep


def to_md(reports, thr):
    L = ["# Informe geométrico (Bambu Lab A1 · cama 256×256×256)", f"Umbral voladizo usado: {thr}° desde la vertical.", ""]
    for r in reports:
        if "error" in r:
            L += [f"## {r['name']} — ERROR: {r['error']}", ""]
            continue
        L.append(f"## {r['name']}")
        L.append(f"- Archivo: `{r['file']}`")
        L.append(f"- Tamaño original: {r['size_as_loaded_mm']} mm · triángulos {r['triangles']} · cuerpos {r['bodies']}")
        L.append(f"- Estanco: {r['watertight']} · volumen {r['volume_cm3']} cm³{'' if r['volume_is_exact'] else ' (aprox. casco convexo)'} · área {r['surface_area_cm2']} cm² · agujeros pasantes (genus): {r['genus_through_holes']}")
        g = r["grams_estimate"]
        L.append(f"- Gramos PLA: sólido {g['PLA']['solid_100%']} g · típico {g['PLA']['typical_2walls_15%']} g | PETG típico {g['PETG']['typical_2walls_15%']} g")
        if r.get("wall_thickness"):
            w = r["wall_thickness"]
            L.append(f"- Grosor pared: p5 {w['p5_mm']} · p25 {w['p25_mm']} · mediana {w['median_mm']} mm · <0.45: {w['frac_below_0.45mm']*100:.1f}% · <0.8: {w['frac_below_0.8mm']*100:.1f}% · <1.2: {w['frac_below_1.2mm']*100:.1f}%")
        for w in r["warnings"]:
            L.append(f"- ⚠️ {w}")
        L.append(f"- Hoja de vistas: `{r['views_png']}`")
        L.append("")
        L.append("| # | Orientación | Tamaño XYZ mm | Contacto cama mm² | Voladizo mm² | Soporte≈cm³ | Esbeltez | Cabe | Score |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for o in r["orientations"]:
            L.append(f"| {o['rank']} | {o['label']} | {o['size_xyz_mm']} | {o['bed_contact_mm2']} | {o['overhang_area_mm2']} | {o['support_volume_est_cm3']} | {o['slenderness_h_over_minxy']} | {'sí' if o['fits_A1'] else 'NO'} | {o['score']} |")
        for o in r["orientations"]:
            if "png" in o:
                L.append(f"- #{o['rank']}: mapa voladizos `{o['png']}` · STL orientado `{o['oriented_stl']}`")
        L.append("")
    L.append("> Score = heurística (menos soporte, menos altura, buen contacto, poca esbeltez). NO considera resistencia ni caras estéticas: eso lo decides tú.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default=None)
    ap.add_argument("--threshold", type=float, default=45.0, help="grados desde la vertical a partir de los que hay voladizo (45 clásico)")
    ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    if not 0 < a.threshold < 90:
        ap.error("--threshold debe estar entre 0 y 90 (excluidos)")
    if not 1 <= a.top <= 12:
        ap.error("--top debe estar entre 1 y 12")
    p = os.path.abspath(a.path)
    if not os.path.exists(p):
        ap.error("La ruta no existe")
    out = os.path.abspath(a.out or os.path.join(p if os.path.isdir(p) else os.path.dirname(p), "_analisis_a1"))
    if os.path.isdir(p) and os.path.normcase(out) == os.path.normcase(p):
        ap.error("--out debe ser una carpeta distinta de la carpeta de modelos")
    files = []
    if os.path.isfile(p):
        if not p.lower().endswith(EXTS):
            ap.error("Formato de modelo no soportado")
        files = [p]
    else:
        for dp, directories, filenames in os.walk(p):
            directories[:] = [d for d in directories if d != "_analisis_a1"
                              and os.path.normcase(os.path.join(dp, d)) != os.path.normcase(out)]
            files.extend(os.path.join(dp, f) for f in filenames if f.lower().endswith(EXTS))
        files.sort()
    if not files:
        print("[ERROR] No hay modelos 3D en", p)
        sys.exit(1)
    os.makedirs(out, exist_ok=True)
    reps = []
    for f in files:
        print(f"[..] {os.path.basename(f)}", flush=True)
        try:
            reps.append(analyze(f, out, a.threshold, a.top))
        except Exception as ex:
            reps.append({"name": os.path.basename(f), "file": f, "error": repr(ex)})
    for r in reps:
        r.pop("_key", None)
    with open(os.path.join(out, "report.json"), "w", encoding="utf-8") as output:
        json.dump(reps, output, indent=1, ensure_ascii=False)
    md = to_md(reps, a.threshold)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as output:
        output.write(md)
    print(md)
    print(f"\n[OK] Salida en: {out}")
    if any("error" in r for r in reps):
        sys.exit(1)


if __name__ == "__main__":
    main()
