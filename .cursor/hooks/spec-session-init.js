#!/usr/bin/env node
// sessionStart hook: primes every Cursor agent session with a brief
// reminder about the Kiro-style spec workflow, plus a snapshot of any
// in-flight specs under specs/.
//
// Contract (https://cursor.com/docs/agent/hooks):
//   - stdin: JSON { session_id, is_background_agent, composer_mode }
//   - stdout: JSON { env?, additional_context? }
//   - exit 0 on success; non-zero exits are logged but do not block
//
// This hook is fire-and-forget: Cursor does not wait on it. Keep it
// fast and dependency-free.

'use strict';

const fs = require('node:fs');
const path = require('node:path');

function readStdinSync() {
  try {
    return fs.readFileSync(0, 'utf8');
  } catch (_err) {
    return '';
  }
}

function safeJSON(text) {
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch (_err) {
    return {};
  }
}

function projectRoot() {
  return process.env.CURSOR_PROJECT_DIR || process.cwd();
}

function listSpecs(root) {
  const specsDir = path.join(root, 'specs');
  if (!fs.existsSync(specsDir)) return [];

  let entries;
  try {
    entries = fs.readdirSync(specsDir, { withFileTypes: true });
  } catch (_err) {
    return [];
  }

  const specs = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;

    const dir = path.join(specsDir, entry.name);
    const has = (name) => fs.existsSync(path.join(dir, name));
    const filled = (name) => {
      try {
        const text = fs.readFileSync(path.join(dir, name), 'utf8');
        // A file is "filled" once the template placeholders are gone.
        // Templates ship with placeholders like {{FEATURE_NAME}},
        // {{REQUIREMENT_TITLE}}, {{trigger}}, {{condition}}, etc.;
        // spec-new.js substitutes the metadata ones (name/date/author)
        // but leaves body placeholders for the human (or AI) to fill
        // in during the matching phase. We detect any remaining
        // {{...}} marker as "not yet filled".
        return !/\{\{[^{}\n]+\}\}/.test(text);
      } catch (_err) {
        return false;
      }
    };

    const status = {
      name: entry.name,
      hasRequirements: has('requirements.md'),
      hasBugfix: has('bugfix.md'),
      hasDesign: has('design.md'),
      hasTasks: has('tasks.md'),
      requirementsFilled: has('requirements.md') && filled('requirements.md'),
      bugfixFilled: has('bugfix.md') && filled('bugfix.md'),
      designFilled: has('design.md') && filled('design.md'),
      tasksFilled: has('tasks.md') && filled('tasks.md'),
      tasksDone: 0,
      tasksTotal: 0,
    };

    if (status.hasTasks && status.tasksFilled) {
      try {
        const tasks = fs.readFileSync(path.join(dir, 'tasks.md'), 'utf8');
        const checkboxes = tasks.match(/^- \[[ x~]\]/gm) || [];
        status.tasksTotal = checkboxes.length;
        status.tasksDone = (tasks.match(/^- \[x\]/gm) || []).length;
      } catch (_err) {
        // ignore unreadable tasks.md
      }
    }

    specs.push(status);
  }
  return specs;
}

function specPhase(s) {
  // A fresh scaffold has all three files but none filled yet → phase 1.
  // Each phase is "complete" only once its primary artifact is filled.
  if (!s.hasRequirements && !s.hasBugfix) return 'phase 0 (setup)';
  if (!s.requirementsFilled && !s.bugfixFilled) {
    return s.hasBugfix ? 'phase 1 (bugfix spec)' : 'phase 1 (requirements)';
  }
  if (!s.hasDesign || !s.designFilled) return 'phase 2 (design)';
  if (!s.hasTasks || !s.tasksFilled) return 'phase 3 (tasks)';
  if (s.tasksTotal === 0) return 'phase 3 (tasks — empty)';
  if (s.tasksDone < s.tasksTotal) {
    return `phase 4 (impl ${s.tasksDone}/${s.tasksTotal})`;
  }
  return 'complete';
}

function buildContext(specs) {
  const lines = [];
  lines.push('## Spec session reminder');
  lines.push('');
  lines.push(
    'This project uses Kiro-style spec-driven development. Before ' +
      'writing implementation code for any non-trivial feature or bug, ' +
      'run a spec session: requirements.md → design.md → tasks.md, ' +
      'one phase at a time, with user approval between phases. The ' +
      'full protocol lives in `.cursor/rules/spec-sessions.mdc`.'
  );
  lines.push('');
  lines.push(
    'Trigger: when the user asks to build / design / implement / refactor ' +
      'something that touches more than one file, switch to plan mode and ' +
      'announce a spec session. Use ' +
      '`node .cursor/scripts/spec-new.js <feature-name>` to scaffold.'
  );

  if (specs.length > 0) {
    lines.push('');
    lines.push('### Existing specs under `specs/`');
    lines.push('');
    for (const s of specs) {
      lines.push(`- \`specs/${s.name}/\` — ${specPhase(s)}`);
    }
    lines.push('');
    lines.push(
      'If the user is asking about one of these, resume that spec at the ' +
        'phase shown rather than starting a new one.'
    );
  } else {
    lines.push('');
    lines.push(
      'No specs exist yet under `specs/`. Create one when the next ' +
        'multi-file feature or non-trivial bug arrives.'
    );
  }

  return lines.join('\n');
}

function main() {
  const input = safeJSON(readStdinSync());

  // Background subagents inherit context from their parent and don't
  // need this primer. Skip to keep their context lean.
  if (input.is_background_agent === true) {
    process.stdout.write(JSON.stringify({}));
    process.exit(0);
  }

  const root = projectRoot();
  const specs = listSpecs(root);
  const additional_context = buildContext(specs);

  const output = { additional_context };
  process.stdout.write(JSON.stringify(output));
  process.exit(0);
}

try {
  main();
} catch (err) {
  // Hook failures must not break the session. Log and exit 0.
  process.stderr.write(`[spec-session-init] ${err && err.message}\n`);
  process.stdout.write(JSON.stringify({}));
  process.exit(0);
}
