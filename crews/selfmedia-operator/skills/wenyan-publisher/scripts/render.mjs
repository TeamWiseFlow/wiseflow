#!/usr/bin/env node
/**
 * render.mjs — Multi-platform Markdown renderer
 *
 * Renders a Markdown file to platform-optimized HTML using @wenyan-md/core.
 *
 * Usage:
 *   node render.mjs -f article.md [options]
 *
 * Options:
 *   -f, --file <path>         Markdown file (required, or use stdin)
 *   --platform <name>         wechat | zhihu | toutiao | medium  (default: wechat)
 *   -t, --theme <id>          Rendering theme ID (default: default)
 *   -h, --highlight <id>      Code highlight theme (default: solarized-light)
 *   --no-mac-style            Disable Mac-style code blocks
 *   --no-footnote             Disable link-to-footnote conversion
 *   -o, --output <path>       Write HTML to file instead of stdout
 *   --help                    Show this help
 *
 * Output: processed HTML on stdout (or to --output file)
 * Errors: to stderr, exit code 1
 *
 * Platform post-processing:
 *   wechat   — themed HTML, ready to paste into WeChat GZH editor
 *   zhihu    — MathJax formulas → <img data-eeimg alt="formula">
 *   toutiao  — MathJax SVGs → inline data:image/svg+xml img
 *   medium   — blockquote/code/table/math normalization
 *
 * Install dependencies first:
 *   npm install   (in skills/wenyan-render/)
 */

import { parseArgs } from 'node:util';
import { readFile, writeFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
import { renderStyledContent } from '@wenyan-md/core/wrapper';
import { getContentForZhihu, getContentForToutiao, getContentForMedium } from '@wenyan-md/core';

// ── Argument parsing ───────────────────────────────────────────────────────────

const PLATFORMS = ['wechat', 'zhihu', 'toutiao', 'medium'];

const { values } = parseArgs({
  options: {
    file:           { type: 'string',  short: 'f' },
    platform:       { type: 'string',  default: 'wechat' },
    theme:          { type: 'string',  short: 't', default: 'default' },
    highlight:      { type: 'string',  short: 'h', default: 'solarized-light' },
    'custom-theme': { type: 'string',  short: 'c' },
    'no-mac-style': { type: 'boolean', default: false },
    'no-footnote':  { type: 'boolean', default: false },
    output:         { type: 'string',  short: 'o' },
    help:           { type: 'boolean', default: false },
  },
  allowPositionals: true,
  strict: false,
});

if (values.help) {
  console.log(`Usage: node render.mjs -f <file.md> [options]

Options:
  -f, --file <path>         Markdown file path (required)
  --platform <name>         ${PLATFORMS.join(' | ')}  (default: wechat)
  -t, --theme <id>          Theme ID (default: default)
  -h, --highlight <id>      Code highlight theme (default: solarized-light)
  -c, --custom-theme <path> Custom theme CSS file path
  --no-mac-style            Disable Mac-style code blocks
  --no-footnote             Disable link-to-footnote conversion
  -o, --output <path>       Write to file instead of stdout`);
  process.exit(0);
}

if (!values.file) {
  console.error('Error: --file (-f) is required');
  process.exit(1);
}

if (!PLATFORMS.includes(values.platform)) {
  console.error(`Error: unsupported platform "${values.platform}". Supported: ${PLATFORMS.join(', ')}`);
  process.exit(1);
}

// ── Main ───────────────────────────────────────────────────────────────────────

try {
  const markdown = await readFile(values.file, 'utf-8');

  // Step 1: render Markdown → styled HTML (WeChat theme applied)
  const styled = await renderStyledContent(markdown, {
    theme:        values.theme,
    highlight:    values.highlight,
    customTheme:  values['custom-theme'],
    macStyle:     !values['no-mac-style'],
    footnote:     !values['no-footnote'],
  });

  let html;

  if (values.platform === 'wechat') {
    html = styled.content;
  } else {
    // Step 2: apply platform-specific post-processing via jsdom
    const dom = new JSDOM(`<!DOCTYPE html><html><body><section id="wenyan">${styled.content}</section></body></html>`);
    const element = dom.window.document.getElementById('wenyan');

    switch (values.platform) {
      case 'zhihu':
        html = getContentForZhihu(element);
        break;
      case 'toutiao':
        html = getContentForToutiao(element);
        break;
      case 'medium':
        html = getContentForMedium(element);
        break;
    }
  }

  if (values.output) {
    await writeFile(values.output, html, 'utf-8');
    console.error(`Output written to: ${values.output}`);
  } else {
    process.stdout.write(html);
  }
} catch (err) {
  console.error('Error:', err.message || err);
  process.exit(1);
}
