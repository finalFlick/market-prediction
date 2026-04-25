#!/usr/bin/env node
// Scaffold a new spec folder from .cursor/spec-templates/.
//
// Usage:
//   node .cursor/scripts/spec-new.js <feature-name>           # feature spec
//   node .cursor/scripts/spec-new.js <bug-name> --bugfix      # bug spec
//
// Behavior:
//   - Validates <name> is kebab-case, [a-z0-9-]+
//   - Refuses to overwrite an existing specs/<name>/ directory
//   - For features: copies requirements.md, design.md, tasks.md
//   - For bugs:     copies bugfix.md,       design.md, tasks.md
//   - Substitutes {{FEATURE_NAME}}, {{BUG_NAME}}, {{DATE}}, {{AUTHOR}}
//
// Exits 0 on success, non-zero on validation failure.

'use strict';

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');

const FEATURE_FILES = ['requirements.md', 'design.md', 'tasks.md'];
const BUGFIX_FILES = ['bugfix.md', 'design.md', 'tasks.md'];

function fail(msg) {
  process.stderr.write(`spec-new: ${msg}\n`);
  process.exit(1);
}

function isKebabCase(name) {
  return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name);
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function detectAuthor() {
  if (process.env.CURSOR_USER_EMAIL) return process.env.CURSOR_USER_EMAIL;
  if (process.env.GIT_AUTHOR_NAME) return process.env.GIT_AUTHOR_NAME;
  if (process.env.USER) return process.env.USER;
  if (process.env.USERNAME) return process.env.USERNAME;
  return os.userInfo().username || 'unknown';
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = { name: null, bugfix: false };
  for (const a of args) {
    if (a === '--bugfix' || a === '-b') {
      opts.bugfix = true;
    } else if (a === '--help' || a === '-h') {
      printHelp();
      process.exit(0);
    } else if (a.startsWith('-')) {
      fail(`unknown flag: ${a}`);
    } else if (opts.name === null) {
      opts.name = a;
    } else {
      fail(`unexpected positional argument: ${a}`);
    }
  }
  return opts;
}

function printHelp() {
  process.stdout.write(
    [
      'Usage:',
      '  node .cursor/scripts/spec-new.js <name>            # feature spec',
      '  node .cursor/scripts/spec-new.js <name> --bugfix   # bug spec',
      '',
      'Names must be kebab-case (a-z, 0-9, hyphens).',
      '',
    ].join('\n')
  );
}

function fillTemplate(text, vars) {
  return text
    .replace(/\{\{FEATURE_NAME\}\}/g, vars.name)
    .replace(/\{\{BUG_NAME\}\}/g, vars.name)
    .replace(/\{\{DATE\}\}/g, vars.date)
    .replace(/\{\{AUTHOR\}\}/g, vars.author)
    .replace(/\{\{REPORTER\}\}/g, vars.author)
    .replace(/\{\{REVIEWERS\}\}/g, '')
    .replace(/\{\{STAKEHOLDERS\}\}/g, '');
}

function projectRoot() {
  return process.env.CURSOR_PROJECT_DIR || process.cwd();
}

function main() {
  const opts = parseArgs(process.argv);
  if (!opts.name) {
    printHelp();
    fail('missing <name>');
  }
  if (!isKebabCase(opts.name)) {
    fail(
      `invalid name "${opts.name}". Use kebab-case ` +
        '(lowercase letters, digits, hyphens; e.g. binance-orderbook-ingest).'
    );
  }

  const root = projectRoot();
  const templatesDir = path.join(root, '.cursor', 'spec-templates');
  if (!fs.existsSync(templatesDir)) {
    fail(`templates directory not found: ${templatesDir}`);
  }

  const specDir = path.join(root, 'specs', opts.name);
  if (fs.existsSync(specDir)) {
    fail(
      `spec already exists: ${path.relative(root, specDir)} ` +
        '(refusing to overwrite). Edit it in place or pick a new name.'
    );
  }

  fs.mkdirSync(specDir, { recursive: true });

  const files = opts.bugfix ? BUGFIX_FILES : FEATURE_FILES;
  const vars = {
    name: opts.name,
    date: todayISO(),
    author: detectAuthor(),
  };

  const written = [];
  for (const filename of files) {
    const templateName =
      filename === 'requirements.md'
        ? 'requirements-template.md'
        : filename === 'bugfix.md'
        ? 'bugfix-template.md'
        : filename === 'design.md'
        ? 'design-template.md'
        : 'tasks-template.md';

    const src = path.join(templatesDir, templateName);
    const dst = path.join(specDir, filename);
    if (!fs.existsSync(src)) {
      fail(`missing template: ${path.relative(root, src)}`);
    }
    const raw = fs.readFileSync(src, 'utf8');
    fs.writeFileSync(dst, fillTemplate(raw, vars), 'utf8');
    written.push(path.relative(root, dst).replace(/\\/g, '/'));
  }

  const phaseLabel = opts.bugfix ? 'bugfix' : 'feature';
  process.stdout.write(
    [
      `Scaffolded ${phaseLabel} spec: specs/${opts.name}/`,
      ...written.map((p) => `  + ${p}`),
      '',
      'Next steps (per .cursor/rules/spec-sessions.mdc):',
      `  1. Fill in ${opts.bugfix ? 'bugfix.md' : 'requirements.md'} (Phase 1).`,
      '  2. Get user approval, then fill in design.md (Phase 2).',
      '  3. Get user approval, then fill in tasks.md (Phase 3).',
      '  4. Execute tasks one at a time (Phase 4).',
      '',
    ].join('\n')
  );
}

try {
  main();
} catch (err) {
  fail(err && err.message ? err.message : String(err));
}
