import { lstat, mkdir, mkdtemp, readdir, copyFile, rename, rm } from 'node:fs/promises';
import { homedir } from 'node:os';
import { resolve, join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

export const name = '3d-maestro';
export const root = fileURLToPath(new URL('../', import.meta.url));
export const agents = { codex: '.codex', 'claude-code': '.claude', cursor: '.cursor', agents: '.agents' };

export function destination(options, env = process.env, home = homedir(), cwd = process.cwd()) {
  if (options.global && options.project) throw new Error('--global y --project son excluyentes.');
  if (options.dir && (options.global || options.project || options.agent)) {
    throw new Error('--dir es una ruta de skills independiente; no lo combines con --agent/--global/--project.');
  }
  if (options.dir) return join(resolve(cwd, options.dir), name);
  const agent = options.agent ?? 'codex';
  if (!Object.hasOwn(agents, agent)) throw new Error(`Agente desconocido: ${agent}. Opciones: ${Object.keys(agents).join(', ')}`);
  const base = options.project ? join(cwd, agents[agent])
    : agent === 'codex' && env.CODEX_HOME ? resolve(env.CODEX_HOME) : join(home, agents[agent]);
  return join(base, 'skills', name);
}

async function exists(path) {
  try { return await lstat(path); } catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

async function assertNoSymlinks(path) {
  for (let part = resolve(path); ; part = dirname(part)) {
    if ((await exists(part))?.isSymbolicLink()) throw new Error(`Destino con enlace simbólico: ${part}. Usa su ruta real con --dir.`);
    if (part === dirname(part)) break;
  }
}

export async function install(options) {
  const target = destination(options);
  await assertNoSymlinks(target);
  const current = await exists(target);
  if (current && !current.isDirectory()) throw new Error(`El destino no es una carpeta: ${target}`);
  if (current && !options.force) throw new Error(`Ya existe ${target}. Usa --force para actualizar conservando una copia.`);
  if (options['dry-run']) return { target, dryRun: true, backup: current ? 'se creará al instalar' : null };
  await mkdir(dirname(target), { recursive: true });
  const staging = await mkdtemp(join(dirname(target), `.${name}-install-`));
  let backup;
  try {
    for (const file of ['SKILL.md', 'requirements.txt', 'requirements-step.txt', 'LICENSE', 'NOTICE']) {
      await copyFile(join(root, file), join(staging, file));
    }
    for (const [directory, extension] of [['scripts', '.py'], ['references', '.md']]) {
      await mkdir(join(staging, directory));
      for (const file of await readdir(join(root, directory), { withFileTypes: true })) {
        if (file.isFile() && file.name.endsWith(extension)) {
          await copyFile(join(root, directory, file.name), join(staging, directory, file.name));
        }
      }
    }
    if (current) {
      backup = `${target}.backup-${Date.now()}-${process.pid}`;
      await rename(target, backup);
    }
    try { await rename(staging, target); }
    catch (error) { if (backup) await rename(backup, target); throw error; }
    return { target, backup };
  } finally {
    // Only remove the unique staging directory created by this invocation.
    await rm(staging, { recursive: true, force: true });
  }
}
