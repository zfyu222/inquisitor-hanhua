"""Strict Inquisitor validation plus generic checks with one documented visible-text exception."""
import csv
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare_translation import RULES


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python TranslateFiles/validate_inquisitor.py HEADERLESS_TRANSLATION.csv')
    target = Path(sys.argv[1]).resolve()
    def read(path):
        with path.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.reader(handle))
        if any(len(row) != 1 for row in rows):
            raise ValueError('Not a single-column CSV')
        return [row[0] for row in rows]
    source_path = ROOT / 'inquisitor_text.csv'
    source, translation = read(source_path), read(target)
    if len(source) != len(translation):
        raise ValueError('Record counts differ')
    for record, (s, t) in enumerate(zip(source, translation), 1):
        if not t.strip():
            raise ValueError(f'Empty translation at {record}')
        for name, pattern in RULES:
            if re.findall(pattern, s) != re.findall(pattern, t):
                raise ValueError(f'{name} mismatch at {record}')
    print('Project strict validation: all', len(source), 'records passed.')
    module_path = ROOT.parents[1] / '.agents/skills/game-translate/scripts/validate_translation.py'
    spec = importlib.util.spec_from_file_location('inquisitor_generic_validator', module_path)
    generic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generic)
    src_angle, dst_angle = generic.FAMILIES['angle']
    # Only <New Save \> inside the escaped UI label is excluded from the generic
    # machine-tag family. The strict rules above still require both boundaries.
    visible = '<New Save \\>'
    generic.FAMILIES['angle'] = (re.compile('(?!' + re.escape(visible) + ')' + src_angle.pattern), dst_angle)
    report_dir = ROOT / 'TranslateFiles/repair_20261013_v2/generic_profile'
    sys.argv = [str(module_path), str(source_path), str(target), '--src-col', '0', '--dst-col', '0',
                '--report-dir', str(report_dir), '--backup-dir', str(ROOT / 'TranslateFiles/backups')]
    return generic.main()


if __name__ == '__main__':
    raise SystemExit(main())
