import test from 'node:test';
import assert from 'node:assert/strict';
import { buildServer, codexToml, codexConfigPath } from '../lib/printer.js';
import { join, resolve } from 'node:path';

const ok = { host: '192.168.1.50', serial: '0309AB123456789', token: '12345678', model: 'a1' };

test('buildServer genera la entrada MCP con el entorno del usuario', () => {
  const server = buildServer(ok);
  assert.deepEqual(server.args, ['-y', 'bambu-printer-mcp']);
  assert.equal(server.env.BAMBU_TOKEN, '12345678');
  assert.equal(server.env.BAMBU_MODEL, 'a1');
});

test('buildServer rechaza datos inválidos', () => {
  assert.throws(() => buildServer({ ...ok, host: '1.2.3.4; rm -rf' }), /host/);
  assert.throws(() => buildServer({ ...ok, serial: 'x' }), /serie/);
  assert.throws(() => buildServer({ ...ok, token: '' }), /acceso/);
  assert.throws(() => buildServer({ ...ok, model: 'zzz' }), /Modelo/);
});

test('codexToml produce una sección TOML válida', () => {
  const toml = codexToml(buildServer(ok));
  assert.match(toml, /^\[mcp_servers\.bambu-printer\]/);
  assert.match(toml, /args = \["-y", "bambu-printer-mcp"\]/);
  assert.match(toml, /PRINTER_HOST = "192\.168\.1\.50"/);
});

test('codexConfigPath respeta CODEX_HOME', () => {
  assert.equal(codexConfigPath({ CODEX_HOME: '/c/codex' }, '/h'), join(resolve('/c/codex'), 'config.toml'));
  assert.equal(codexConfigPath({}, '/h'), join('/h', '.codex', 'config.toml'));
});
