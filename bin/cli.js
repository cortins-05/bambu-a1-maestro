#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { install, root } from '../lib/installer.js';
import { doctor } from '../lib/doctor.js';

const help = `Bambu A1 Maestro — skill de impresión 3D para agentes IA

Uso: bambu-a1-maestro [install|doctor] [opciones]

  --global             Instalar para todos tus proyectos (por defecto)
  --project            Instalar en el proyecto actual
  --agent NOMBRE       codex (defecto), claude-code, cursor, agents
  --dir RUTA           Directorio skills personalizado (añade bambu-a1-maestro)
  --force              Actualizar conservando una copia de la carpeta anterior
  --dry-run            Mostrar destino sin escribir (install)
  --python RUTA        Intérprete Python a comprobar (doctor)
  --check-auth         Comprobar sesión y cuaderno en NotebookLM (doctor, red)
  --profile NOMBRE     Perfil nlm, por defecto BAMBU_NOTEBOOK_PROFILE o default
  --notebook UUID      Cuaderno a comprobar; también BAMBU_NOTEBOOK_ID
  --json               Salida estructurada de doctor
  --version            Versión
  --help               Ayuda

Instalar no descarga Python, Bambu Studio ni nlm. Requisitos y autenticación:
https://github.com/cortins-05/bambu-a1-maestro#requisitos
`;

try {
  const { values, positionals } = parseArgs({ allowPositionals: true, strict: true, options: {
    global: { type: 'boolean' }, project: { type: 'boolean' }, agent: { type: 'string' },
    dir: { type: 'string' }, force: { type: 'boolean' }, 'dry-run': { type: 'boolean' },
    python: { type: 'string' }, 'check-auth': { type: 'boolean' }, profile: { type: 'string' },
    notebook: { type: 'string' }, json: { type: 'boolean' }, version: { type: 'boolean' }, help: { type: 'boolean' },
  } });
  if (values.help) console.log(help);
  else if (values.version) console.log(JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version);
  else {
    const command = positionals[0] ?? 'install';
    if (positionals.length > 1 || !['install', 'doctor'].includes(command)) throw new Error('Comando desconocido. Usa --help.');
    const allowed = command === 'install' ? ['global', 'project', 'agent', 'dir', 'force', 'dry-run']
      : ['global', 'project', 'agent', 'dir', 'python', 'check-auth', 'profile', 'notebook', 'json'];
    for (const key of Object.keys(values)) if (!allowed.includes(key)) throw new Error(`--${key} no se aplica a ${command}.`);
    if (command === 'install') {
      const result = await install(values);
      console.log(`${result.dryRun ? 'Destino previsto' : 'Skill instalada'}: ${result.target}`);
      if (result.backup) console.log(`Copia anterior: ${result.backup}`);
      console.log('Reabre tu agente para cargar la skill. Ejecuta doctor y completa los requisitos del README.');
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
