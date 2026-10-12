#!/usr/bin/env python3
"""
bambu_slice.py — Lamina de verdad con Bambu Studio (CLI headless) usando los perfiles OFICIALES del A1.
Sirve para VALIDAR la configuración propuesta: tiempo real, gramos, capas, avisos del laminador.

Uso típico:
  python bambu_slice.py pieza.stl --process "0.20mm Standard" --filament "Bambu PLA Basic" \
        --plate textured --set wall_loops=3 --set sparse_infill_density=20% --set enable_support=1
  (el PNG del CLI no funciona en Bambu Studio 2.x: usa los renders de analyze_models.py)
  python bambu_slice.py --list filament PETG       # lista perfiles A1 que contienen "PETG"
  python bambu_slice.py --list process             # lista perfiles de proceso A1
  python bambu_slice.py --show process "0.20mm Standard"   # vuelca todos los valores resueltos
  python bambu_slice.py --show filament "Bambu PETG HF" --keys nozzle_temperature,fan_max_speed

Opciones clave:
  --nozzle 0.4|0.2|0.6|0.8   (defecto 0.4)
  --plate textured|smooth|cool|supertack|engineering   (textured = Textured PEI, smooth = High Temp/Smooth PEI)
  --orient                  deja que Bambu auto-oriente (por defecto NO: usa la orientación del archivo,
                            p.ej. el STL orientado que exporta analyze_models.py)
  --set clave=valor         sobreescribe cualquier ajuste de proceso O filamento (repetible)
  --keep                    conserva el .gcode completo en la carpeta de salida

Salida: imprime JSON resumen y lo guarda en <outdir>/slice_summary.json
Localiza Bambu Studio automáticamente; si no, define BAMBU_STUDIO=<ruta al ejecutable>.
"""
import argparse
import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

try:  # consolas Windows cp1252 no soportan emojis/acentos
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PLATES = {
    "textured": "Textured PEI Plate",
    "smooth": "High Temp Plate",
    "pei": "High Temp Plate",
    "cool": "Cool Plate",
    "supertack": "Supertack Plate",
    "engineering": "Engineering Plate",
}


# ------------------------------------------------------------ localizar Bambu Studio
def find_exe():
    env = os.environ.get("BAMBU_STUDIO")
    if env and os.path.exists(env):
        return env
    cands = []
    sysname = platform.system()
    if sysname == "Windows":
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", ""),
                     os.path.expandvars(r"%LOCALAPPDATA%\Programs")):
            if base:
                cands.append(os.path.join(base, "Bambu Studio", "bambu-studio.exe"))
    elif sysname == "Darwin":
        cands.append("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
    else:
        cands += [shutil.which("bambu-studio") or "", shutil.which("BambuStudio") or ""]
        cands += glob.glob(os.path.expanduser("~/*Bambu*Studio*.AppImage")) + glob.glob("/opt/bambu*/bin/bambu-studio")
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def find_profiles(exe):
    env = os.environ.get("BAMBU_PROFILES")
    if env and os.path.isdir(env):
        return env
    d = os.path.dirname(exe)
    for p in (os.path.join(d, "resources", "profiles", "BBL"),
              os.path.join(d, "..", "Resources", "profiles", "BBL"),
              os.path.join(d, "..", "share", "BambuStudio", "profiles", "BBL")):
        if os.path.isdir(p):
            return os.path.abspath(p)
    return None


# ------------------------------------------------------------ perfiles
class Profiles:
    def __init__(self, root):
        self.root = root
        self.idx = {}
        for sub in ("machine", "process", "filament"):
            for f in os.listdir(os.path.join(root, sub)):
                if not f.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(root, sub, f), encoding="utf-8") as source:
                        d = json.load(source)
                except Exception:
                    continue
                d["_kind"] = sub
                self.idx[d.get("name", f[:-5])] = d

    def resolve(self, name):
        d = self.idx[name]
        out = {}
        if d.get("inherits"):
            out.update(self.resolve(d["inherits"]))
        out.update(d)
        return out

    def a1_names(self, kind, nozzle):
        tag_other = "A1 mini"
        res = []
        for n, d in self.idx.items():
            if d["_kind"] != kind or d.get("instantiation") == "false" or "@base" in n:
                continue
            if "@BBL A1" not in n or tag_other in n or "A1M" in n:
                continue
            nz = re.search(r"(0\.[2468]) nozzle", n)
            if nozzle == "0.4":
                if nz and nz.group(1) != "0.4":
                    continue
            elif not nz or nz.group(1) != nozzle:
                continue
            res.append(n)
        return sorted(res)

    def pick(self, kind, query, nozzle):
        names = self.a1_names(kind, nozzle)
        if query in names:
            return query
        q = query.lower()
        exact = [n for n in names if n.lower().split(" @")[0] == q]
        if exact:
            return exact[0]
        part = [n for n in names if q in n.lower()]
        if part:
            return sorted(part, key=len)[0]
        raise SystemExit(f"[ERROR] No hay perfil {kind} A1 (boquilla {nozzle}) que coincida con '{query}'. "
                         f"Usa --list {kind} para ver opciones.")


def machine_name(nozzle):
    return f"Bambu Lab A1 {nozzle} nozzle"


def coerce(value, old):
    """Mantiene el formato del perfil: si el original era lista, guarda lista."""
    if isinstance(old, list):
        return [value] * max(len(old), 1)
    return value


def write_flat(d, path):
    d = {k: v for k, v in d.items() if not k.startswith("_")}
    d.pop("inherits", None)
    d["from"] = "system"
    with open(path, "w", encoding="utf-8") as output:
        json.dump(d, output, indent=1, ensure_ascii=False)


# ------------------------------------------------------------ salida gcode
HDR = {
    "model_time": r"; model printing time: (.+?); total estimated time: (.+)",
    "layers": r"; total layer number: (\d+)",
    "length_mm": r"; total filament length \[mm\] : ([\d.]+)",
    "weight_g": r"; total filament weight \[g\] : ([\d.]+)",
    "max_z": r"; max_z_height: ([\d.]+)",
}


def parse_gcode(path):
    info = {}
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = "".join(fh.readline() for _ in range(400))
    for k, rx in HDR.items():
        m = re.search(rx, head)
        if m:
            info[k] = m.groups() if len(m.groups()) > 1 else m.group(1)
    if "model_time" in info:
        info["model_print_time"], info["total_time"] = info.pop("model_time")
    return info


def read_gcode_config(path):
    cfg = {}
    # Bambu escribe el bloque "; CONFIG_BLOCK_START ... END" al principio del gcode
    with open(path, encoding="utf-8", errors="ignore") as fh:
        inside = False
        for i, line in enumerate(fh):
            if "CONFIG_BLOCK_START" in line:
                inside = True
                continue
            if "CONFIG_BLOCK_END" in line or (not inside and i > 3000):
                break
            m = re.match(r"^; ([a-zA-Z0-9_]+) = (.*)$", line.rstrip())
            if inside and m:
                cfg[m.group(1)] = m.group(2).strip()
    return cfg


def norm(v):
    v = str(v).strip().strip('"')
    try:
        return f"{float(v.rstrip('%')):g}" + ("%" if v.endswith("%") else "")
    except ValueError:
        return v.split(",")[0].strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("models", nargs="*")
    ap.add_argument("--process", default="0.20mm Standard")
    ap.add_argument("--filament", default="Bambu PLA Basic")
    ap.add_argument("--nozzle", default="0.4", choices=["0.2", "0.4", "0.6", "0.8"])
    ap.add_argument("--plate", default="textured", choices=list(PLATES))
    ap.add_argument("--set", action="append", default=[], metavar="clave=valor")
    ap.add_argument("--orient", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--list", nargs="+", metavar=("KIND", "FILTRO"))
    ap.add_argument("--show", nargs=2, metavar=("KIND", "NOMBRE"))
    ap.add_argument("--keys", default=None)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    exe = find_exe()
    if not exe:
        print(json.dumps({"ok": False, "error": "Bambu Studio no encontrado. Instálalo o define BAMBU_STUDIO."}))
        sys.exit(3)
    prof_root = find_profiles(exe)
    if not prof_root:
        print(json.dumps({"ok": False, "error": "Carpeta de perfiles BBL no encontrada. Define BAMBU_PROFILES."}))
        sys.exit(3)
    P = Profiles(prof_root)

    if a.list:
        kind = a.list[0]
        filt = " ".join(a.list[1:]).lower()
        names = P.a1_names(kind, a.nozzle) if kind != "machine" else [n for n in P.idx if n.startswith("Bambu Lab A1 ") and "mini" not in n and "template" not in n]
        for n in names:
            if filt in n.lower():
                print(n)
        return
    if a.show:
        kind, q = a.show
        name = machine_name(a.nozzle) if kind == "machine" else P.pick(kind, q, a.nozzle)
        r = P.resolve(name)
        keys = a.keys.split(",") if a.keys else sorted(r)
        print(f"# {name}")
        for k in keys:
            if k in r and "gcode" not in k and not k.startswith("_"):
                v = r[k]
                print(f"{k} = {v[0] if isinstance(v, list) and len(v) == 1 else v}")
        return
    if not a.models:
        ap.error("Falta al menos un modelo")
    if a.timeout <= 0:
        ap.error("--timeout debe ser positivo")
    for model in a.models:
        if not os.path.isfile(model):
            ap.error(f"Modelo no encontrado: {model}")

    mname = machine_name(a.nozzle)
    pname = P.pick("process", a.process, a.nozzle)
    fname = P.pick("filament", a.filament, a.nozzle)
    mach, proc, fil = P.resolve(mname), P.resolve(pname), P.resolve(fname)
    proc["curr_bed_type"] = PLATES[a.plate]

    applied, unknown = {}, []
    for kv in a.set:
        if "=" not in kv:
            ap.error(f"Ajuste inválido: {kv}. Usa --set clave=valor")
        k, v = kv.split("=", 1)
        k, v = k.strip(), v.strip()
        if k in proc:
            proc[k] = coerce(v, proc[k]); applied[k] = v
        elif k in fil:
            fil[k] = coerce(v, fil[k]); applied[k] = v
        elif k in mach:
            mach[k] = coerce(v, mach[k]); applied[k] = v
        else:
            ap.error(f"Clave desconocida: {k}. Consulta --show process/filament/machine antes de modificarla.")

    outdir = os.path.abspath(a.outdir or os.path.join(os.path.dirname(os.path.abspath(a.models[0])), "_analisis_a1", "slice"))
    os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="bbl_")
    mj, pj, fj = (os.path.join(tmp, n) for n in ("machine.json", "process.json", "filament.json"))
    write_flat(mach, mj)
    write_flat(proc, pj)
    write_flat(fil, fj)
    work = os.path.join(tmp, "out")
    os.makedirs(work)

    cmd = [exe, "--debug", "1", "--orient", "1" if a.orient else "0", "--arrange", "1",
           "--load-settings", f"{mj};{pj}", "--load-filaments", fj,
           "--slice", "0", "--outputdir", work]
    cmd += [os.path.abspath(m) for m in a.models]
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=a.timeout)
        rc = cp.returncode
        log = (cp.stdout or "")[-3000:] + (cp.stderr or "")[-3000:]
    except subprocess.TimeoutExpired:
        rc, log = -999, "timeout"

    summary = {"ok": False, "exe_rc": rc, "machine": mname, "process": pname, "filament": fname,
               "plate": PLATES[a.plate], "overrides": applied, "unknown_keys_passed_raw": unknown}
    rj = os.path.join(work, "result.json")
    if os.path.exists(rj):
        with open(rj, encoding="utf-8") as source:
            res = json.load(source)
        summary["slicer_return_code"] = res.get("return_code")
        summary["slicer_error"] = res.get("error_string")
        plates = []
        for pl in res.get("sliced_plates", []):
            ft = pl.get("feature_type_times", {})
            plates.append({
                "plate": pl.get("id"),
                "total_time_s": round(pl.get("total_predication", 0)),
                "total_time_h": round(pl.get("total_predication", 0) / 3600, 2),
                "filament_g": round(sum(f.get("total_used_g", 0) for f in pl.get("filaments", [])), 2),
                "filament_changes": pl.get("filament_change_times"),
                "objects": [{"name": o.get("name"), "bbox_wdh": [round(o["bbox"]["width"], 1), round(o["bbox"]["depth"], 1), round(o["bbox"]["height"], 1)]} for o in pl.get("objects", []) if "bbox" in o],
                "time_by_feature_s": {k: round(v) for k, v in sorted(ft.items(), key=lambda x: -x[1]) if v >= 1},
                "warning": pl.get("warning_message") or "",
            })
        summary["plates"] = plates
        summary["ok"] = bool(plates) and rc == 0 and res.get("return_code", 0) == 0
    g = sorted(glob.glob(os.path.join(work, "*.gcode")))
    if g:
        summary["gcode_header"] = parse_gcode(g[0])
        # verificar que cada override quedó en el gcode (valores inválidos se sustituyen EN SILENCIO)
        cfg = read_gcode_config(g[0])
        check, bad = {}, []
        for k, v in applied.items():
            got = cfg.get(k)
            check[k] = got
            if got is None or norm(got) != norm(v):
                bad.append(f"{k}: pedido '{v}' -> gcode '{got}'")
        summary["overrides_in_gcode"] = check
        if bad:
            summary["OVERRIDE_MISMATCH"] = bad
        if a.keep:
            for f in g:
                shutil.copy(f, outdir)
    for f in glob.glob(os.path.join(work, "*.png")):
        shutil.copy(f, outdir)
        summary.setdefault("png", []).append(os.path.join(outdir, os.path.basename(f)))
    if not summary["ok"]:
        summary["log_tail"] = log[-1500:]
    if applied and not g:
        summary["OVERRIDE_MISMATCH"] = ["No se generó G-code para verificar los ajustes solicitados."]
    if summary.get("OVERRIDE_MISMATCH"):
        summary["ok"] = False
    with open(os.path.join(outdir, "slice_summary.json"), "w", encoding="utf-8") as output:
        json.dump(summary, output, indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    shutil.rmtree(tmp, ignore_errors=True)
    if not summary["ok"]:
        sys.exit(2 if summary.get("OVERRIDE_MISMATCH") else 1)


if __name__ == "__main__":
    main()
