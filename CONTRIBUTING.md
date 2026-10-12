# Contribuir

Abre una issue con el problema, sistema operativo, versión de Python y Bambu Studio, boquilla, material y un modelo mínimo que puedas compartir. Elimina rutas privadas, identificadores de cuadernos y credenciales de los informes.

Para desarrollar, clona el repositorio, ejecuta `npm ci` e instala `requirements.txt` en un entorno virtual. Antes de enviar un pull request:

```bash
npm run check
npm test
python -m unittest discover -s tests -p "test_*.py"
npm pack --dry-run
```

Los tests Python usan modelos sintéticos temporales; no necesitan una impresora, Bambu Studio ni una sesión Google. Los tests del instalador usan directorios temporales, sin tocar las skills personales.

Para cambios en el laminador, valida además una pieza sintética con una instalación real de Bambu Studio. Indica versión, perfil, ajustes y si aparecieron discrepancias. No atribuyas resultados de calidad física a un test de software.

Conserva el instalador sin dependencias npm ni scripts automáticos de instalación. Cada ajuste técnico de las referencias debe indicar su contexto y diferenciar datos oficiales, observaciones y heurísticas.

## Releases

1. Actualiza `package.json`, `package-lock.json`, `SKILL.md`, `CHANGELOG.md` y las etiquetas de los ejemplos del README.
2. Ejecuta las comprobaciones y una instalación desde el tarball producido por `npm pack` en un directorio temporal.
3. Crea una etiqueta `vX.Y.Z` sobre el commit verificado y publícala.
4. Crea una GitHub Release con el tarball y su SHA-256. Verifica el comando `npx` desde la etiqueta pública.

La distribución por GitHub no requiere publicar en npm. Una publicación futura en el registro debería usar una cuenta del mantenedor, 2FA y trusted publishing con procedencia; no guardes tokens en workflows.
