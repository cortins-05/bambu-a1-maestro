#!/usr/bin/env python3
"""Local read-only environment diagnostics. Never accesses NotebookLM credentials."""
import importlib
import json
import os
import sys

from bambu_slice import find_exe, find_profiles


def check():
    checks = [{"name": "Python", "ok": sys.version_info >= (3, 11),
               "detail": sys.version.split()[0] + " (requerido: 3.11+)"}]
    for module in ("trimesh", "numpy", "matplotlib", "scipy", "rtree", "networkx", "lxml"):
        try:
            importlib.import_module(module)
            checks.append({"name": module, "ok": True, "detail": "Disponible en este intérprete."})
        except Exception:
            checks.append({"name": module, "ok": False, "detail": "Instala requirements.txt con este intérprete."})
    exe = find_exe()
    profiles = find_profiles(exe) if exe else None
    checks.append({"name": "Bambu Studio", "ok": bool(exe), "detail": exe or "Instálalo o define BAMBU_STUDIO."})
    valid = bool(profiles and all(os.path.isdir(os.path.join(profiles, sub)) for sub in ("machine", "process", "filament")))
    checks.append({"name": "Perfiles BBL", "ok": valid, "detail": profiles or "Define BAMBU_PROFILES apuntando a profiles/BBL."})
    return checks


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False))
