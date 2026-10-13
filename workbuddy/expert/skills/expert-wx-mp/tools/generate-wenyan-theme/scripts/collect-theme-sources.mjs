#!/usr/bin/env node
// Prepare user-provided HTML for layout analysis; no network or account lookup.
import { readFile, stat, realpath, mkdir, writeFile, rename, unlink } from 'node:fs/promises';
import { resolve, relative, isAbsolute, dirname, basename, extname, join } from 'node:path';
import { randomUUID } from 'node:crypto';

const HELP = 'generate-wenyan-theme --input-html <local.html> [--input-html <another.html>] [--output wx_mp/wenyan-theme/sources.json]';
const within = (root, target) => {
  const name = relative(root, target);
  return name !== '..' && !name.startsWith('../') && !name.startsWith('..\\') && !isAbsolute(name);
};

async function main(argv) {
  if (argv.length === 1 && ['--help', '-h'].includes(argv[0])) {
    console.log(HELP);
    return;
  }
  const inputs = [];
  let output = 'wx_mp/wenyan-theme/sources.json';
  for (let i = 0; i < argv.length; i++) {
    const option = argv[i];
    if (!['--input-html', '--output'].includes(option)) throw new Error('LOCAL_HTML_ONLY: ' + HELP);
    const value = argv[++i];
    if (!value || value.startsWith('--')) throw new Error('ARGUMENT_REQUIRED: ' + option);
    if (option === '--input-html') inputs.push(value);
    else output = value;
  }
  if (!inputs.length) throw new Error('LOCAL_HTML_REQUIRED: ' + HELP);
  if (isAbsolute(output) || output.split(/[\\/]/).includes('..') || extname(output).toLowerCase() !== '.json') {
    throw new Error('WORKSPACE_RELATIVE_JSON_REQUIRED');
  }
  const workspace = await realpath(resolve(process.env.XIAOBEI_WORKSPACE || process.cwd()));
  const destination = resolve(workspace, output);
  if (!within(workspace, destination)) throw new Error('OUTPUT_OUTSIDE_WORKSPACE');
  const articles = [];
  const seen = new Set();
  for (const input of inputs) {
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(input)) throw new Error('LOCAL_HTML_REQUIRED');
    const path = await realpath(resolve(workspace, input));
    if (seen.has(path)) continue;
    const info = await stat(path);
    if (!info.isFile() || !['.html', '.htm'].includes(extname(path).toLowerCase())) throw new Error('HTML_FILE_REQUIRED');
    if (info.size === 0 || info.size > 10 * 1024 * 1024) throw new Error('HTML_FILE_SIZE_INVALID');
    const content = await readFile(path, 'utf8');
    if (!content.trim()) throw new Error('HTML_CONTENT_EMPTY');
    articles.push({ title: basename(path), source_file: path, content_html: content, provided_by: 'user' });
    seen.add(path);
  }
  let ancestor = dirname(destination);
  while (true) {
    try {
      if (!within(workspace, await realpath(ancestor))) throw new Error('OUTPUT_OUTSIDE_WORKSPACE');
      break;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      ancestor = dirname(ancestor);
    }
  }
  await mkdir(dirname(destination), { recursive: true });
  if (!within(workspace, await realpath(dirname(destination)))) throw new Error('OUTPUT_OUTSIDE_WORKSPACE');
  const temporary = join(dirname(destination), '.sources-' + randomUUID() + '.tmp');
  try {
    const document = { ok: true, mode: 'provided-content', total: articles.length, articles };
    await writeFile(temporary, JSON.stringify(document, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
    await rename(temporary, destination);
  } finally {
    await unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error; });
  }
  console.log(JSON.stringify({ ok: true, mode: 'provided-content', total: articles.length, output: destination }));
}

try {
  await main(process.argv.slice(2));
} catch (error) {
  console.log(JSON.stringify({ ok: false, error: error.message }));
  process.exitCode = 1;
}
