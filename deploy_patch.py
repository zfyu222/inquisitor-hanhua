"""Install/remove only the known localization overlay; preserve original archives."""
import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'Repack'
GAME = (ROOT/'Game/Game').resolve()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require_closed():
    output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq Inquisitor.exe', '/FO', 'CSV', '/NH'])
    names = [row[0].lower() for row in csv.reader(io.StringIO(output.decode('mbcs', errors='replace'))) if row]
    if 'inquisitor.exe' in names:
        raise SystemExit('Close Inquisitor before installing, removing or restoring settings.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['install','remove','restore-settings','status'])
    args = parser.parse_args()
    destination = GAME/'03_zh.dat'
    report = json.loads((WORK/'build_report.json').read_text(encoding='utf-8'))
    deployment_path = WORK/'deployment.json'
    deployment = json.loads(deployment_path.read_text(encoding='utf-8')) if deployment_path.exists() else {}
    if args.action == 'status':
        current = None
        locked = False
        if destination.exists():
            try:
                current = digest(destination)
            except PermissionError:
                locked = True
        print(json.dumps(dict(path=str(destination), installed=destination.exists(),
                              current_sha256=current, locked_by_running_game=locked,
                              last_installed_sha256=deployment.get('overlay_sha256'),
                              candidate_sha256=report['overlay_sha256']), indent=2))
        return
    require_closed()
    # Detect changes in the original files rather than silently accepting a new build.
    for name, expected in deployment.get('original_sha256', {}).items():
        assert digest(GAME/name) == expected, f'Original game file changed: {name}'
    if args.action == 'restore-settings':
        for name, before, after in [('gfx.ini','CreateLogFile=0','CreateLogFile=1'), ('d3dparams.ini','StartWindowed=0','StartWindowed=1')]:
            saved = WORK/(name+'.original')
            if saved.exists():
                original = saved.read_bytes()
                expected = original.replace(before.encode(),after.encode())
                current = (GAME/name).read_bytes()
                accepted = [original,expected]
                if name == 'd3dparams.ini':
                    size_backup = WORK/'d3dparams.ini.window-size.original'
                    if size_backup.exists() and size_backup.read_bytes() == expected:
                        accepted.append(expected.replace(b'InitialScreenWidth=1024',b'InitialScreenWidth=2048').replace(b'InitialScreenHeight=768',b'InitialScreenHeight=1536'))
                assert current in accepted, f'{name} was changed separately; refusing overwrite.'
                (GAME/name).write_bytes(original)
                print('Restored', name)
        return
    if destination.exists():
        expected = {report['overlay_sha256'], deployment.get('overlay_sha256')}
        assert digest(destination) in expected, 'Unknown 03_zh.dat; refusing to replace or remove it.'
        if args.action == 'install' and digest(destination) == report['overlay_sha256']:
            print('Already installed and verified.')
            return
        backup_dir = WORK/'backups'
        backup_dir.mkdir(exist_ok=True)
        backup = backup_dir/f'03_zh_{datetime.now():%Y%m%d_%H%M%S}.dat'
        assert not backup.exists()
        shutil.copy2(destination, backup)
        destination.unlink()
        print('Saved old overlay to', backup)
    if args.action == 'remove':
        print('Overlay removed; original archives preserved.')
        return
    candidate = WORK/'Files/Game/03_zh.dat'
    assert digest(candidate) == report['overlay_sha256']
    with destination.open('xb') as output:
        output.write(candidate.read_bytes())
    assert digest(destination) == report['overlay_sha256']
    deployment.update(path=str(destination), overlay_sha256=report['overlay_sha256'], installed_at=datetime.now().isoformat())
    deployment_path.write_text(json.dumps(deployment,indent=2), encoding='utf-8')
    print('Installed and verified:', destination)

if __name__ == '__main__':
    main()
