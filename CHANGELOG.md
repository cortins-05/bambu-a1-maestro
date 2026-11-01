# Changelog

## 1.1.0 — 2026-11-01

- Proyecto renombrado a 3D-maestro (paquete, comando, carpeta de skill y repositorio). Si tenías `bambu-a1-maestro` instalada, borra esa carpeta y reinstala.
- Nuevo comando `printer`: registra el MCP de impresión LAN (`bambu-printer-mcp`) en Claude Code, Codex o Cursor con los datos de cada usuario.
- SKILL.md: paso opcional de impresión con confirmación explícita antes de iniciar.

## 1.0.0 — 2026-10-12

- Primera distribución pública de la skill 3D-maestro.
- Instalación global o por proyecto vía npx desde una etiqueta de GitHub; Codex, Claude Code, Cursor y destino genérico.
- Instalador sin dependencias npm, comprobación de destino, previsualización y actualización con copia de seguridad.
- Diagnóstico de Python, paquetes, Bambu Studio, perfiles BBL, skill NotebookLM y CLI nlm; comprobación de sesión/cuaderno optativa.
- NotebookLM configurable por usuario, sin identificadores privados incluidos.
- Análisis geométrico, renders, orientación y laminado con perfiles oficiales instalados.
- Corrección de colisiones de nombres, errores que antes devolvían éxito y validación de overrides/perfiles A1.
- Requisitos reproducibles por rangos, documentación de instalación y pruebas automatizadas.
