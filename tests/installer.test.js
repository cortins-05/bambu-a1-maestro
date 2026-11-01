import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, access, rm, mkdir, symlink, realpath } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { install, destination, root } from '../lib/installer.js';

async function workspace(t) {
  const path = await realpath(await mkdtemp(join(tmpdir(), 'bambu test ')));
  t.after(() => rm(path, { recursive: true, force: true }));
  return path;
}

test('global, project, custom and CODEX_HOME destinations', () => {
  assert.equal(destination({}, {}, '/users/test', '/project'), join('/users/test', '.codex', 'skills', '3d-maestro'));
  assert.equal(destination({ global: true }, { CODEX_HOME: '/custom/codex' }), join(resolve('/custom/codex'), 'skills', '3d-maestro'));
  assert.equal(destination({ project: true, agent: 'claude-code' }, {}, '/users/test', '/project'), join('/project', '.claude', 'skills', '3d-maestro'));
  assert.throws(() => destination({ global: true, project: true }), /excluyentes/);
  assert.throws(() => destination({ agent: '../escape' }), /desconocido/);
  assert.throws(() => destination({ dir: 'skills', agent: 'codex' }), /no lo combines/);
});

test('fresh installation includes runtime assets, not developer files', async t => {
  const dir = await workspace(t);
  const { target } = await install({ dir });
  for (const file of ['SKILL.md', 'scripts/analyze_models.py', 'scripts/bambu_slice.py', 'scripts/check_environment.py', 'references/recetario_ajustes.md', 'requirements.txt', 'LICENSE']) {
    await access(join(target, file));
  }
  await assert.rejects(access(join(target, 'tests')));
  await assert.rejects(access(join(target, 'scripts/__pycache__')));
  assert.match(await readFile(join(target, 'SKILL.md'), 'utf8'), /BAMBU_NOTEBOOK_ID/);
});

test('dry-run writes nothing', async t => {
  const dir = join(await workspace(t), 'missing');
  const result = await install({ dir, 'dry-run': true });
  assert.equal(result.dryRun, true);
  await assert.rejects(access(dir));
});

test('existing installation is protected, force preserves all local changes', async t => {
  const dir = await workspace(t);
  const first = await install({ dir });
  await writeFile(join(first.target, 'my-local-notes.md'), 'personal notes');
  await writeFile(join(first.target, 'SKILL.md'), 'custom skill');
  await assert.rejects(install({ dir }), /Ya existe/);
  const next = await install({ dir, force: true });
  assert.equal(await readFile(join(next.backup, 'SKILL.md'), 'utf8'), 'custom skill');
  assert.equal(await readFile(join(next.backup, 'my-local-notes.md'), 'utf8'), 'personal notes');
  assert.match(await readFile(join(next.target, 'SKILL.md'), 'utf8'), /name: 3d-maestro/);
  await assert.rejects(access(join(next.target, 'my-local-notes.md')));
});

test('symlink/junction destinations cannot modify their target', async t => {
  const dir = await workspace(t);
  const real = join(dir, 'real');
  await mkdir(real);
  await writeFile(join(real, 'sentinel'), 'unchanged');
  const linked = join(dir, 'linked');
  await symlink(real, linked, process.platform === 'win32' ? 'junction' : 'dir');
  await assert.rejects(install({ dir: linked, force: true }), /simbólico/);
  assert.equal(await readFile(join(real, 'sentinel'), 'utf8'), 'unchanged');
});

test('CLI reports invalid options and supports help/version without side effects', () => {
  const cli = join(root, 'bin/cli.js');
  for (const args of [['--agent', 'invalid'], ['--unknown'], ['erase'], ['install', '--check-auth']]) {
    const result = spawnSync(process.execPath, [cli, ...args], { encoding: 'utf8' });
    assert.equal(result.status, 1, result.stdout + result.stderr);
  }
  const help = spawnSync(process.execPath, [cli, '--help'], { encoding: 'utf8' });
  assert.equal(help.status, 0);
  assert.match(help.stdout, /--global/);
  const version = spawnSync(process.execPath, [cli, '--version'], { encoding: 'utf8' });
  assert.equal(version.status, 0);
  assert.equal(version.stdout.trim(), '1.1.0');
});
