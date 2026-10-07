#!/usr/bin/env python3
"""Dependency-free repository validation. Does not approve hardware."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {'To Do', 'In Progress', 'Blocked', 'Done'}


def metadata(text):
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise ValueError('missing frontmatter')
    block = text.split('---', 2)[1]
    return dict(line.split(':', 1) for line in block.strip().splitlines() if ':' in line)


def validate(root=ROOT):
    errors = []
    tasks = {}
    for path in sorted((root / '.tasks/items').glob('*.md')):
        try:
            text = path.read_text()
            data = {k.strip(): v.strip() for k, v in metadata(text).items()}
            for key in ('id', 'title', 'status', 'milestone', 'sprint', 'depends_on', 'updated'):
                if not data.get(key):
                    raise ValueError(f'missing {key}')
            if path.stem != data['id'] or not re.fullmatch(r'[A-Z]+-\d{3}', data['id']):
                raise ValueError('invalid ID/path')
            if data['status'] not in STATUSES:
                raise ValueError('invalid status')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['updated']):
                raise ValueError('invalid date')
            if data['sprint'] != 'backlog' and not (root / '.tasks/sprints' / (data['sprint'] + '.md')).exists():
                raise ValueError('missing sprint')
            criteria = text.split('## Critérios de aceite\n', 1)[1].split('\n## ', 1)[0]
            if not re.search(r'^- \[[ x]\] ', criteria, re.M):
                raise ValueError('missing acceptance checklist')
            if data['status'] == 'Done' and '- [ ]' in criteria:
                raise ValueError('Done with unchecked acceptance criteria')
            tasks[data['id']] = data
        except (ValueError, IndexError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
    if not tasks:
        errors.append('no tasks')
    edges = {}
    for ident, data in tasks.items():
        edges[ident] = [] if data['depends_on'] == 'none' else [s.strip() for s in data['depends_on'].split(',')]
        for dep in edges[ident]:
            if dep not in tasks:
                errors.append(f'{ident}: unknown dependency {dep}')
            elif data['status'] in {'In Progress', 'Done'} and tasks[dep]['status'] != 'Done':
                errors.append(f'{ident}: dependency {dep} not Done')
    visiting, visited = set(), set()

    def visit(ident):
        if ident in visiting:
            errors.append(f'dependency cycle: {ident}')
            return
        if ident in visited:
            return
        visiting.add(ident)
        for dep in edges.get(ident, []):
            visit(dep)
        visiting.remove(ident)
        visited.add(ident)

    for ident in tasks:
        visit(ident)
    if sum(d['status'] == 'In Progress' for d in tasks.values()) > 2:
        errors.append('WIP exceeds 2')
    for path in sorted((root / 'skills').glob('*/SKILL.md')):
        try:
            data = {k.strip(): v.strip() for k, v in metadata(path.read_text()).items()}
            if data.get('name') != path.parent.name or not data.get('description'):
                raise ValueError('invalid skill name/description')
            ev = json.loads(path.with_name('evals.json').read_text())
            if ev.get('skill_name') != path.parent.name or len(ev.get('evals', [])) < 2:
                raise ValueError('missing eval cases')
            for case in ev['evals']:
                if not case.get('prompt') or not case.get('expected_output'):
                    raise ValueError('invalid eval case')
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
    for link, target in [('CLAUDE.md', 'AGENTS.md'), ('.claude/skills', 'skills'), ('.agents/skills', 'skills')]:
        path = root / link
        if not path.is_symlink() or path.resolve() != (root / target).resolve():
            errors.append(f'{link}: expected canonical symlink to {target}')
    for path in root.rglob('*.md'):
        relative = path.relative_to(root)
        if any(p.startswith('.') for p in relative.parts if p not in {'.tasks', '.github'}):
            continue
        if str(relative).startswith(('docs/archive/', 'build/')):
            continue
        for dest in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', path.read_text()):
            if dest.startswith(('http:', 'https:', 'mailto:', '#')):
                continue
            dest = dest.split('#', 1)[0]
            if dest and not (path.parent / dest).exists():
                errors.append(f'{relative}: broken link {dest}')
    return errors


if __name__ == '__main__':
    failures = validate()
    for error in failures:
        print('ERROR:', error)
    print(f'Repository validation: {len(failures)} error(s); NOT hardware sign-off')
    sys.exit(bool(failures))
