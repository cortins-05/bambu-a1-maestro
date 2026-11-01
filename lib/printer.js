import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { createInterface } from 'node:readline/promises';

// Servidor MCP comunitario (npm: bambu-printer-mcp). Habla con la impresora en LAN por MQTT + FTPS.
export const serverName = 'bambu-printer';
export const serverPackage = 'bambu-printer-mcp';
export const models = ['a1', 'a1-mini', 'p1s', 'p1p', 'x1c', 'x1e', 'h2d'];
export const printerAgents = ['claude-code', 'codex', 'cursor'];

export function buildServer({ host, serial, token, model }) {
  if (!/^[0-9a-zA-Z.:-]+$/.test(host ?? '')) throw new Error('IP o host de la impresora no válido.');
  if (!/^[0-9A-Za-z]{8,32}$/.test(serial ?? '')) throw new Error('Número de serie no válido (se ve en la impresora: Ajustes > Dispositivo).');
  if (!/^[0-9A-Za-z]{6,32}$/.test(token ?? '')) throw new Error('Código de acceso LAN no válido.');
  if (!models.includes(model)) throw new Error(`Modelo desconocido: ${model}. Opciones: ${models.join(', ')}`);
  return {
    command: 'npx', args: ['-y', serverPackage],
    env: { PRINTER_HOST: host, BAMBU_MODEL: model, BAMBU_SERIAL: serial, BAMBU_TOKEN: token },
  };
}

const q = value => JSON.stringify(value);

export function codexToml(server) {
  const env = Object.entries(server.env).map(([k, v]) => `${k} = ${q(v)}`).join(', ');
  return `[mcp_servers.${serverName}]\ncommand = ${q(server.command)}\nargs = [${server.args.map(q).join(', ')}]\nenv = { ${env} }\n`;
}

export function codexConfigPath(env = process.env, home = homedir()) {
  return join(env.CODEX_HOME ? resolve(env.CODEX_HOME) : join(home, '.codex'), 'config.toml');
}

async function readOr(path, fallback) {
  try { return await readFile(path, 'utf8'); } catch (error) { if (error.code === 'ENOENT') return fallback; throw error; }
}

async function ask(rl, label, current) {
  if (current) return current;
  return (await rl.question(`${label}: `)).trim();
}

export async function collect(options, env = process.env) {
  const given = {
    host: options.host ?? env.PRINTER_HOST ?? env.BAMBU_PRINTER_HOST,
    serial: options.serial ?? env.BAMBU_SERIAL ?? env.BAMBU_PRINTER_SERIAL,
    token: options.token ?? env.BAMBU_TOKEN ?? env.BAMBU_PRINTER_ACCESS_TOKEN,
    model: options.model ?? env.BAMBU_MODEL ?? env.BAMBU_PRINTER_MODEL ?? 'a1',
  };
  if (given.host && given.serial && given.token) return given;
  if (!process.stdin.isTTY) throw new Error('Faltan datos: usa --host, --serial y --token (o variables PRINTER_HOST, BAMBU_SERIAL, BAMBU_TOKEN).');
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    given.host = await ask(rl, 'IP de la impresora (Ajustes > Red)', given.host);
    given.serial = await ask(rl, 'Número de serie', given.serial);
    given.token = await ask(rl, 'Código de acceso LAN (Ajustes > Red)', given.token);
  } finally { rl.close(); }
  return given;
}

async function registerClaude(server, dryRun) {
  const args = ['mcp', 'add-json', '--scope', 'user', serverName, JSON.stringify({ type: 'stdio', ...server })];
  if (dryRun) return `claude mcp add-json --scope user ${serverName} <config>`;
  const run = spawnSync('claude', args, { encoding: 'utf8', shell: process.platform === 'win32' });
  if (run.error || run.status !== 0) {
    throw new Error(`No pude ejecutar "claude mcp add-json" (${run.error?.message ?? run.stderr?.trim() ?? run.status}). ` +
      `Si ya existe, quítalo antes con: claude mcp remove ${serverName} --scope user`);
  }
  return 'Claude Code (scope user, ~/.claude.json)';
}

async function registerCodex(server, dryRun, env) {
  const path = codexConfigPath(env);
  if (dryRun) return path;
  const current = await readOr(path, '');
  if (current.includes(`[mcp_servers.${serverName}]`)) {
    throw new Error(`${path} ya define ${serverName}. Edita o borra esa sección y repite.`);
  }
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${current}${current && !current.endsWith('\n') ? '\n' : ''}${current ? '\n' : ''}${codexToml(server)}`);
  return path;
}

async function registerCursor(server, dryRun, home) {
  const path = join(home, '.cursor', 'mcp.json');
  if (dryRun) return path;
  let data;
  try { data = JSON.parse(await readOr(path, '{}')); } catch { throw new Error(`${path} no es JSON válido; corrígelo y repite.`); }
  data.mcpServers ??= {};
  if (data.mcpServers[serverName]) throw new Error(`${path} ya define ${serverName}.`);
  data.mcpServers[serverName] = server;
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(data, null, 2)}\n`);
  return path;
}

export async function setupPrinter(options, env = process.env, home = homedir()) {
  const agent = options.agent ?? 'claude-code';
  if (!printerAgents.includes(agent)) throw new Error(`Agente no soportado para la impresora: ${agent}. Opciones: ${printerAgents.join(', ')}`);
  const server = buildServer(await collect(options, env));
  const dryRun = Boolean(options['dry-run']);
  const where = agent === 'claude-code' ? await registerClaude(server, dryRun)
    : agent === 'codex' ? await registerCodex(server, dryRun, env)
      : await registerCursor(server, dryRun, home);
  return { agent, where, dryRun };
}
