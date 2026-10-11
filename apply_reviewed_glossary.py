"""Check by default; --apply installs reviewed project tables after AINiee exits."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'AiNieeCache' / 'AinieeCacheData.json'
    raw = path.read_bytes()
    cache = json.loads(raw)
    original = json.loads((ROOT / 'glossary_original.json').read_text(encoding='utf-8'))
    reviewed = json.loads((ROOT / 'glossary_reviewed.json').read_text(encoding='utf-8'))
    if hashlib.sha256((ROOT / 'glossary_original.json').read_bytes()).hexdigest() != reviewed['review_metadata']['original_sha256']:
        raise SystemExit('Original glossary snapshot does not match this review.')
    current = cache.get('extra', {}).get('analysis_v1')
    if current == reviewed:
        print('Reviewed glossary is already installed; no files changed.')
        return
    if current != original:
        raise SystemExit('Live glossary changed since review. Re-review it before applying.')
    seen = set()
    for group in ('characters', 'terms'):
        for row in reviewed[group]:
            key = row['source'].casefold()
            if key in seen or not key.strip() or not row['recommended_translation'].strip():
                raise SystemExit('Reviewed glossary contains duplicate or empty fields.')
            seen.add(key)
    print('Validated reviewed entries:', len(seen))
    if not args.apply:
        print('Check only; no files changed. Close AINiee before using --apply.')
        return
    # A running GUI keeps its own cache and can overwrite an external update.
    command = "$ErrorActionPreference='Stop'; @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(python(w)?|AiNiee)\\.exe$' -and ($_.Name -match '^AiNiee' -or $_.CommandLine -match 'AiNiee\\.py') }).Count"
    result = subprocess.run(['powershell', '-NoProfile', '-Command', command], capture_output=True, text=True, check=True)
    if int(result.stdout.strip()) != 0:
        raise SystemExit('AINiee is running. Close it before applying the review.')
    backup_dir = path.parent / 'glossary_review_backups'
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / ('AinieeCacheData_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.json')
    backup.write_bytes(raw)
    revised = copy.deepcopy(cache)
    revised['extra']['analysis_v1'] = reviewed
    temporary = path.with_name(path.name + '.review.tmp')
    temporary.write_text(json.dumps(revised, ensure_ascii=False, indent=2), encoding='utf-8')
    if path.read_bytes() != raw:
        temporary.unlink()
        raise SystemExit('Cache changed during preparation; aborted. Original backup retained.')
    os.replace(temporary, path)
    print('Applied. Backup:', backup)
    print('Reopen AINiee and inspect the project analysis table.')


if __name__ == '__main__':
    main()
