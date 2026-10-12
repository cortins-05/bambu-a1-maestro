import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { root, destination } from './installer.js';

function run(command, args, timeout = 20000) {
  return spawnSync(command, args, { encoding: 'utf8', timeout, windowsHide: true, shell: false });
}

export function doctor(options) {
  const checks = [];
  const add = (name, ok, detail) => checks.push({ name, ok, detail });
  const candidates = options.python ? [options.python] : process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python'];
  const python = candidates.find(command => run(command, ['--version']).status === 0);
  if (python) {
    const result = run(python, [join(root, 'scripts', 'check_environment.py')]);
    try { checks.push(...JSON.parse(result.stdout)); }
    catch { add('Python', false, 'No se pudo ejecutar check_environment.py con este intérprete.'); }
  } else add('Python', false, 'Instala Python 3.11+ o usa --python con la ruta del ejecutable.');
  const target = destination(options);
  add('Skill Bambu A1', existsSync(join(target, 'SKILL.md')), target);
  const bases = [join(homedir(), '.agents', 'skills'), join(homedir(), '.claude', 'skills'),
    join(process.env.CODEX_HOME || join(homedir(), '.codex'), 'skills'), join(homedir(), '.cursor', 'skills'),
    join(target, '..')];
  const hasSkill = bases.some(base => ['notebooklm-cli', 'nlm-skill', 'gemini-notebook'].some(name => existsSync(join(base, name, 'SKILL.md'))));
  add('Skill NotebookLM', hasSkill, 'Debe ser visible para tu agente: nlm skill install agents --level user (Codex) o claude-code.');
  add('CLI nlm', run('nlm', ['--help']).status === 0, 'Instalación independiente: uv tool install notebooklm-mcp-cli');
  if (options['check-auth']) {
    const profile = options.profile || process.env.BAMBU_NOTEBOOK_PROFILE || 'default';
    // Suppress account/cookie output; a failed check can also mean a network error.
    const auth = run('nlm', ['login', '--check', '--profile', profile], 45000);
    add('Autenticación NotebookLM', auth.status === 0, auth.status === 0 ? 'Sesión verificada.' : 'No verificada: comprueba red y nlm login --check; inicia sesión si caducó.');
    const notebook = options.notebook || process.env.BAMBU_NOTEBOOK_ID;
    if (auth.status === 0 && notebook) {
      add('Acceso al cuaderno', run('nlm', ['notebook', 'get', notebook, '--profile', profile], 45000).status === 0,
        'Verifica además el título y que las fuentes sean suficientes.');
    } else add('Acceso al cuaderno', false, 'Usa --notebook UUID o BAMBU_NOTEBOOK_ID y una sesión válida para comprobar acceso.');
  }
  return checks;
}
