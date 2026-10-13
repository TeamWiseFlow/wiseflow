#!/usr/bin/env node
import * as fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { dirname, join, resolve, delimiter, basename } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';

const entry = fileURLToPath(import.meta.url);
const product = resolve(dirname(entry), '../../..');
const index = JSON.parse(await fs.readFile(join(product, '.codebuddy-plugin/native-index.json'), 'utf8'));
const settings = JSON.parse(await fs.readFile(join(product, '.codebuddy-plugin/product.json'), 'utf8'));
const state = resolve(process.env.XIAOBEI_WORKBUDDY_HOME || join(homedir(), '.xiaobei-workbuddy'));
const output = value => process.stdout.write(JSON.stringify(value) + '\n');
const quote = value => "'" + String(value).replaceAll("'", "'\\''") + "'";
const sha = data => createHash('sha256').update(data).digest('hex');
const args = process.argv.slice(2);
let workspace = process.env.XIAOBEI_WORKSPACE || process.cwd();
if (args[0] === '--workspace') { args.shift(); workspace = args.shift(); }
if (!workspace) throw new Error('WORKSPACE_REQUIRED');
workspace = resolve(workspace);
const action = args.shift() || 'doctor';

function run(program, argv, options = {}) {
  const result = spawnSync(program, argv, { encoding: 'utf8', stdio: ['inherit',2,2], ...options });
  if (result.error) throw new Error('RUNTIME_MISSING: ' + basename(program));
  if (result.status !== 0) throw new Error('DEPENDENCY_SETUP_FAILED: ' + basename(program));
  return result;
}
function locate(candidates, argv) {
  return candidates.find(command => {
    const result = spawnSync(command, argv, { encoding: 'utf8', stdio: 'pipe' });
    return !result.error && result.status === 0;
  });
}
const pythonCommand = process.env.XIAOBEI_PYTHON || locate(['python3', 'python'], ['-c', 'import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)']);
const python = pythonCommand ? spawnSync(pythonCommand,['-c','import sys;print(sys.executable)'],{encoding:'utf8',stdio:'pipe'}).stdout.trim() : undefined;
const bash = process.env.XIAOBEI_BASH || locate(['/opt/homebrew/bin/bash', '/usr/local/bin/bash', 'bash'], ['--version']);
let fingerprint;
async function cachePath() {
  if (!fingerprint) {
    const inputs = [
    join(product, '.codebuddy-plugin/native-index.json'), entry,
    join(product, '.codebuddy-plugin/product.json'),
    join(dirname(entry), 'sqlite_cli.py'), join(dirname(entry), '../references/python-requirements.txt'),
    join(dirname(entry), 'import_session.mjs'),
    join(dirname(entry), '../package.json'),
    ];
    fingerprint = sha(Buffer.concat(await Promise.all(inputs.map(path => fs.readFile(path)))));
  }
  return join(state, 'runtimes', fingerprint.slice(0,24));
}
async function prepare() {
  if (Number(process.versions.node.split('.')[0]) < 22 || !python || !bash) throw new Error('RUNTIME_MISSING: Node 22+, Python 3.10+ and Bash are required');
  const root = await cachePath();
  if (existsSync(join(root, '.ready'))) return root;
  await fs.mkdir(root, { recursive: true, mode: 0o700 });
  for (const record of index.files) {
    const from = join(product, 'skills', record.target);
    const bytes = await fs.readFile(from);
    if (sha(bytes) !== record.sha256) throw new Error('PACKAGE_CHANGED: ' + record.target);
    const target = join(root, 'skills', record.target);
    await fs.mkdir(dirname(target), { recursive: true });
    await fs.writeFile(target, bytes, { mode: target.endsWith('.sh') ? 0o755 : 0o644 });
  }
  await fs.cp(join(product, 'skills/xiaobei-runtime'), join(root, 'skills/xiaobei-runtime'), { recursive: true });
  const bin = join(root, 'bin');
  await fs.mkdir(bin, { recursive: true });
  await fs.writeFile(join(bin, 'sqlite3'), '#!/usr/bin/env bash\nexec ' + quote(python) + ' ' + quote(join(root, 'skills/xiaobei-runtime/scripts/sqlite_cli.py')) + ' "$@"\n', { mode: 0o755 });
  for (const command of Object.keys(index.commands)) {
    await fs.writeFile(join(bin, command), '#!/usr/bin/env bash\nexec ' + quote(process.execPath) + ' ' + quote(entry) + ' --workspace "${XIAOBEI_WORKSPACE:?workspace required}" exec ' + quote(command) + ' "$@"\n', { mode: 0o755 });
  }
  for (const name of ['python', 'python3']) await fs.writeFile(join(bin, name), '#!/usr/bin/env bash\nexec ' + quote(python) + ' "$@"\n', { mode: 0o755 });
  await fs.writeFile(join(root, '.ready'), fingerprint);
  return root;
}
async function environment(root) {
  let configured = {};
  try { configured = JSON.parse(await fs.readFile(join(state, 'config.json'), 'utf8')); }
  catch (error) { if (error.code !== 'ENOENT') throw new Error('CONFIG_INVALID'); }
  return { ...process.env, ...configured,
    XIAOBEI_WORKSPACE: workspace, XIAOBEI_NATIVE_ROOT: root, XIAOBEI_WORKBUDDY_HOME: state,
    OPENCLAW_HOME: state, OPENCLAW_STATE_DIR: root,
    PLATFORM_API_HOME: join(state, 'logins/platform-api'),
    RELAY_BASE_URL: configured.RELAY_BASE_URL || process.env.RELAY_BASE_URL || settings.relay_base_url,
    PUBLISHED_TRACK_ROOT: workspace, CONTENT_CALIBRATOR_ROOT: workspace,
    PUBLISHED_TRACK_SCRIPTS: join(root, 'skills/published-track/scripts'),
    PATH: [join(root, 'bin'), dirname(process.execPath), process.env.PATH || ''].join(delimiter),
    PLAYWRIGHT_BROWSERS_PATH: join(state, 'browsers'),
  };
}
async function pythonDependencies(root, env, full = false) {
  const requirements = join(root, 'skills/xiaobei-runtime/references/python-requirements.txt');
  if (!full && existsSync(join(root, '.python-ready'))) return;
  const venv = join(root, 'venv');
  const executable = join(venv, process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  if (!existsSync(executable)) run(python, ['-m', 'venv', venv], { env });
  run(executable, ['-m', 'pip', 'install', '--disable-pip-version-check', '-r', requirements], { env });
  for (const name of ['python', 'python3']) await fs.writeFile(join(root, 'bin', name), '#!/usr/bin/env bash\nexec ' + quote(executable) + ' "$@"\n', { mode: 0o755 });
  await fs.writeFile(join(root, '.python-ready'), 'ready');
}
async function nodeDependencies(root, skill, env) {
  const directory = join(root, 'skills', skill);
  const packageFile = join(directory, 'package.json');
  if (!existsSync(packageFile)) return;
  const pkg = JSON.parse(await fs.readFile(packageFile, 'utf8'));
  if (!Object.keys(pkg.dependencies || {}).length) return;
  const installer = pkg.xiaobei?.dependencyInstaller?.script;
  if (installer) run(process.execPath, [join(directory, installer)], { env, cwd: directory });
  else if (!existsSync(join(directory, '.node-ready')) || !existsSync(join(directory, 'node_modules'))) {
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    run(npm, ['install', '--omit=dev', '--no-audit', '--no-fund'], { cwd: directory, env });
    await fs.writeFile(join(directory, '.node-ready'), 'ready');
  }
}
async function mediaDependencies(root, env) {
  if (locate(['ffmpeg'], ['-version']) && locate(['ffprobe'], ['-version'])) return;
  await nodeDependencies(root, 'xiaobei-runtime', env);
  const directory = join(root, 'skills/xiaobei-runtime');
  const { createRequire } = await import('node:module');
  const require = createRequire(join(directory, 'package.json'));
  const binaries = { ffmpeg: require('ffmpeg-static'), ffprobe: require('ffprobe-static').path };
  for (const [name, path] of Object.entries(binaries)) {
    if (!path) throw new Error('MEDIA_RUNTIME_UNSUPPORTED');
    const target = join(root, 'bin', name + (process.platform === 'win32' ? '.exe' : ''));
    await fs.copyFile(path, target); await fs.chmod(target, 0o755);
  }
}
async function chromiumDependencies(root, env) {
  const chromium = env.CHROME_BIN || locate(['google-chrome', 'chromium', 'chromium-browser', '/opt/google/chrome/chrome', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'], ['--version']);
  if (chromium) {
    const found = spawnSync(python, ['-c','import shutil,sys;print(shutil.which(sys.argv[1]) or sys.argv[1])',chromium], {encoding:'utf8',env});
    if (found.status !== 0) throw new Error('CHROMIUM_UNAVAILABLE');
    return resolve(found.stdout.trim());
  }
  await pythonDependencies(root, env);
  const executable = join(root, 'venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
  run(executable, ['-m', 'playwright', 'install', 'chromium'], { env });
  const result = spawnSync(executable, ['-c', 'from playwright.sync_api import sync_playwright;\np=sync_playwright().start();print(p.chromium.executable_path);p.stop()'], { encoding: 'utf8', env });
  if (result.status !== 0) throw new Error('CHROMIUM_UNAVAILABLE');
  return result.stdout.trim();
}

try {
  if (action === 'list') output({ ok: true, version: index.version, skills: index.skills, commands: index.commands, excluded: index.excluded_paths });
  else if (action === 'doctor') output({ ok: Number(process.versions.node.split('.')[0]) >= 22 && !!python && !!bash, node: process.versions.node, python: python || null, bash: bash || null, workspace, state_home: state, skills: index.skills.length, commands: Object.keys(index.commands).length, default_relay_base_url: settings.relay_base_url });
  else if (action === 'contact') {
    const asset = index.assets.find(record => record.target === settings.contact_image);
    const bytes = await fs.readFile(join(product, settings.contact_image));
    if (!asset || sha(bytes) !== asset.sha256) throw new Error('CONTACT_ASSET_CHANGED');
    const directory = join(workspace,'xiaobei/contact');
    await fs.mkdir(directory,{recursive:true});
    let target = join(directory,'ofb_contact.png');
    if (existsSync(target) && sha(await fs.readFile(target)) !== sha(bytes)) target = join(directory,'ofb_contact-'+sha(bytes).slice(0,12)+'.png');
    if (!existsSync(target)) await fs.writeFile(target,bytes,{flag:'wx'});
    output({ok:true,contact_image:target,vip_club:settings.vip_club,relay_base_url:settings.relay_base_url});
  }
  else if (action === 'configure') {
    if (args.shift() !== '--env-file' || !args[0]) throw new Error('PRIVATE_ENV_FILE_REQUIRED');
    const file = resolve(args[0]), stat = await fs.lstat(file);
    if (!stat.isFile() || stat.isSymbolicLink() || (process.platform !== 'win32' && ((stat.mode & 0o077) || stat.uid !== process.getuid()))) throw new Error('PRIVATE_ENV_FILE_UNSAFE');
    const config = JSON.parse(await fs.readFile(file, 'utf8'));
    if (!config || Array.isArray(config) || Object.entries(config).some(([k,v]) => !/^[A-Z][A-Z0-9_]*$/.test(k) || typeof v !== 'string' || ['PATH','HOME','OPENCLAW_HOME','OPENCLAW_STATE_DIR','XIAOBEI_WORKSPACE','XIAOBEI_NATIVE_ROOT'].includes(k))) throw new Error('ENV_FORMAT_INVALID');
    await fs.mkdir(state, { recursive: true, mode: 0o700 });
    await fs.writeFile(join(state, 'config.json'), JSON.stringify(config), { mode: 0o600 });
    await fs.chmod(join(state, 'config.json'), 0o600); output({ ok: true, configured: Object.keys(config) });
  } else if (action === 'setup' || action === 'exec' || action === 'import-session') {
    const root = await prepare();
    let env = await environment(root);
    if (action === 'import-session') {
      await nodeDependencies(root, 'platform-runtime', env);
      const result = spawnSync(process.execPath, [join(root, 'skills/xiaobei-runtime/scripts/import_session.mjs'), ...args], {env,stdio:'inherit'});
      process.exitCode = result.status ?? 1;
    } else if (action === 'setup') {
      if (args.includes('--full')) {
        await pythonDependencies(root, env, true); await mediaDependencies(root, env);
        for (const skill of index.skills) await nodeDependencies(root, skill, env);
        env.CHROME_BIN = await chromiumDependencies(root, env);
      }
      output({ ok: true, native_root: root, workspace, commands: Object.keys(index.commands).length });
    } else {
      const command = args.shift();
      if (!Object.hasOwn(index.commands, command)) throw new Error('COMMAND_UNAVAILABLE: ' + command);
      const target = index.commands[command], skill = target.split('/')[0];
      const standardOnly = ['published-track','content-calibrator','bd-record','ir-record','video-edit'].includes(command);
      if (!standardOnly && process.env.XIAOBEI_USE_SYSTEM_DEPS !== '1') await pythonDependencies(root, env);
      if (['video-edit','talking-head-cut','viral-chaser','video-review'].includes(command)) await mediaDependencies(root, env);
      if (command === 'native-ui-card' || command.startsWith('pitch-deck-') && command !== 'pitch-deck-extract') env.CHROME_BIN = await chromiumDependencies(root, env);
      await nodeDependencies(root, skill, env);
      if ((await fs.readFile(join(root, 'skills', target), 'utf8')).includes('platform-runtime/')) await nodeDependencies(root, 'platform-runtime', env);
      await fs.mkdir(workspace,{recursive:true});
      const targetArgs = target.endsWith('.py') ? [join(root,'bin/python3'),join(root,'skills',target),...args] : [join(root,'skills',target),...args];
      const result = spawnSync(bash, targetArgs, { cwd: workspace, env, stdio: 'inherit' });
      if (result.error) throw new Error('COMMAND_EXEC_FAILED');
      process.exitCode = result.status ?? 1;
    }
  } else throw new Error('UNKNOWN_ACTION');
} catch (error) {
  output({ ok: false, error: error.message }); process.exitCode = 1;
}
