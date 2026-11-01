#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { install, root } from '../lib/installer.js';
import { doctor } from '../lib/doctor.js';
import { setupPrinter } from '../lib/printer.js';

const help = `3D-maestro — skill de impresión 3D para agentes IA

Uso: 3d-maestro [install|doctor|printer] [opciones]

  --global             Instalar para todos tus proyectos (por defecto)
  --project            Instalar en el proyecto actual
  --agent NOMBRE       codex (defecto), claude-code, cursor, agents
  --dir RUTA           Directorio skills personalizado (añade 3d-maestro)
  --force              Actualizar conservando una copia de la carpeta anterior
  --dry-run            Mostrar destino sin escribir (install)
  --python RUTA        Intérprete Python a comprobar (doctor)
  --check-auth         Comprobar sesión y cuaderno en NotebookLM (doctor, red)
  --profile NOMBRE     Perfil nlm, por defecto BAMBU_NOTEBOOK_PROFILE o default
  --notebook UUID      Cuaderno a comprobar; también BAMBU_NOTEBOOK_ID
  --json               Salida estructurada de doctor
  --host IP            (printer) IP de la impresora en tu red
  --serial SN          (printer) Número de serie
  --token CODIGO       (printer) Código de acceso LAN
  --model MODELO       (printer) a1 (defecto), a1-mini, p1s, p1p, x1c, x1e, h2d
  --version            Versión
  --help               Ayuda

Comando printer: registra el servidor MCP de impresión (LAN) en claude-code, codex o cursor.
Sin --host/--serial/--token los pregunta. Requiere Modo solo LAN y Modo desarrollador en la impresora.

Instalar no descarga Python, Bambu Studio ni nlm. Requisitos y autenticación:
https://github.com/cortins-05/3D-maestro#requisitos
`;

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, strict: true, options: {
    global: { type: 'boolean' }, project: { type: 'boolean' }, agent: { type: 'string' },
    dir: { type: 'string' }, force: { type: 'boolean' }, 'dry-run': { type: 'boolean' },
    python: { type: 'string' }, 'check-auth': { type: 'boolean' }, profile: { type: 'string' },
    notebook: { type: 'string' }, host: { type: 'string' }, serial: { type: 'string' }, token: { type: 'string' }, model: { type: 'string' }, json: { type: 'boolean' }, version: { type: 'boolean' }, help: { type: 'boolean' },
  } });
  if (values.help) console.log(help);
  else if (values.version) console.log(JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version);
  else {
    const command = positionals[0] ?? 'install';
    if (positionals.length > 1 || !['install', 'doctor', 'printer'].includes(command)) throw new Error('Comando desconocido. Usa --help.');
    const allowed = command === 'printer' ? ['agent', 'host', 'serial', 'token', 'model', 'dry-run']
      : command === 'install' ? ['global', 'project', 'agent', 'dir', 'force', 'dry-run']
      : ['global', 'project', 'agent', 'dir', 'python', 'check-auth', 'profile', 'notebook', 'json'];
    for (const key of Object.keys(values)) if (!allowed.includes(key)) throw new Error(`--${key} no se aplica a ${command}.`);
    if (command === 'install') {
      const result = await install(values);
      console.log(`${result.dryRun ? 'Destino previsto' : 'Skill instalada'}: ${result.target}`);
      if (result.backup) console.log(`Copia anterior: ${result.backup}`);
      console.log('Reabre tu agente para cargar la skill. Ejecuta doctor y completa los requisitos del README.');
    } else if (command === 'printer') {
      const result = await setupPrinter(values);
      console.log(`${result.dryRun ? 'Se registraría' : 'Impresora registrada'} para ${result.agent}: ${result.where}`);
      console.log('Reinicia el agente. El código de acceso queda guardado en esa configuración local; no la compartas.');
    } else {
      const checks = doctor(values);
      if (values.json) console.log(JSON.stringify({ ok: checks.every(c => c.ok), authenticationChecked: Boolean(values['check-auth']), checks }, null, 2));
      else {
        for (const check of checks) console.log(`[${check.ok ? 'OK' : 'PENDIENTE'}] ${check.name}: ${check.detail}`);
        if (!values['check-auth']) console.log('Autenticación y cuaderno no comprobados. Añade --check-auth --notebook UUID.');
      }
      if (checks.some(c => !c.ok)) process.exitCode = 1;
    }
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exitCode = 1;
}
