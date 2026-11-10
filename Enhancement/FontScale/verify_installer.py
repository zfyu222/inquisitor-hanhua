"""Exercise the shipped ZIP against isolated copies, without deploying to the game."""
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    archive = HERE/'Inquisitor_独立增强补丁_字体可选.zip'
    work = HERE/'verification'
    work.mkdir(exist_ok=True)
    # Keep diagnostic copies under the ignored directory; never modify real game files.
    root = Path(tempfile.mkdtemp(prefix='installer_',dir=work))
    game = root/'game root with spaces'
    (game/'Game').mkdir(parents=True)
    package = root/'package'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        z.extractall(package)
    manifest = json.loads((package/'PATCH_MANIFEST.json').read_text(encoding='utf-8'))
    options = {o['percent']:o for o in manifest['options']}
    real = (PROJECT/'Game/Game').resolve()
    before = {str(p):sha(p) for p in [real/'Inquisitor.exe',real/'03_zh.dat']}
    real_enhancements = {p.name:sha(p) for p in real.glob('04_enhancement*.dat')}
    shutil.copy2(real/'Inquisitor.exe',game/'Game/Inquisitor.exe')
    shutil.copy2(PROJECT/'Repack/Files/Game/03_zh.dat',game/'Game/03_zh.dat')
    target = game/manifest['target']
    legacy = game/manifest['legacy_target']
    script = package/'manage.ps1'
    results = []
    def run(label,action='install',scale=None,stdin=None,expected=0,auto=False):
        cmd = ['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Action',action]
        if not auto: cmd += ['-GameRoot',str(game)]
        if scale is not None: cmd += ['-Scale',str(scale)]
        r = subprocess.run(cmd,input=stdin,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
        assert r.returncode == expected,(label,r.stdout,r.stderr)
        results.append(dict(check=label,expected=expected,exit_code=r.returncode))
    def installed(percent):
        assert target.exists() and sha(target)==options[percent]['sha256']
        assert not legacy.exists()
    # Repeated swaps exercise replacement, including all directions and idempotence.
    for percent in [125,150,200,125,200,150,150]:
        run(f'select {percent}',scale=percent); installed(percent)
    run('uninstall',action='uninstall'); assert not target.exists()
    run('repeat uninstall',action='uninstall')
    for choice,percent in [('1',125),('2',150),('3',200)]:
        run(f'interactive {percent}',stdin=choice+'\n'); installed(percent)
    previous=sha(target)
    run('interactive cancel',stdin='0\n'); assert sha(target)==previous
    run('invalid menu input then 125',stdin='wrong\n1\n'); installed(125)
    run('interactive restore 100',stdin='4\n'); assert not target.exists()
    legacy_source=PROJECT/'Enhancement/Font125/Files/Game/04_enhancement_font125.dat'
    for percent in [125,150,200]:
        if target.exists(): target.unlink()
        shutil.copy2(legacy_source,legacy)
        run(f'migrate legacy to {percent}',scale=percent); installed(percent)
    # Known new+old coexistence is normalized to one selected overlay.
    shutil.copy2(legacy_source,legacy)
    run('remove known duplicate legacy',scale=150); installed(150)
    # Source corruption is rejected before replacing the current scale.
    payload=package/options[200]['payload']; saved=payload.read_bytes(); payload.write_bytes(b'corrupt')
    run('reject corrupt candidate',scale=200,expected=1); installed(150); payload.write_bytes(saved)
    target.write_bytes(b'unknown')
    run('reject unknown current install',scale=125,expected=1)
    run('reject unknown current uninstall',action='uninstall',expected=1)
    assert target.read_bytes()==b'unknown'; target.unlink()
    legacy.write_bytes(b'unknown legacy')
    run('reject unknown legacy install',scale=125,expected=1)
    run('reject unknown legacy uninstall',action='uninstall',expected=1)
    assert legacy.read_bytes()==b'unknown legacy' and not target.exists(); legacy.unlink()
    chinese=game/'Game/03_zh.dat'; saved=chinese.read_bytes(); chinese.unlink()
    run('reject missing localization',scale=125,expected=1); assert not target.exists()
    chinese.write_bytes(b'wrong version')
    run('reject unknown localization',scale=125,expected=1); assert not target.exists(); chinese.write_bytes(saved)
    exe=game/'Game/Inquisitor.exe'; saved=exe.read_bytes(); exe.write_bytes(b'wrong executable')
    run('reject unsupported executable',scale=125,expected=1); assert not target.exists(); exe.write_bytes(saved)
    # Menu and auto-location from a package extracted into the installation root.
    for p in package.iterdir():
        if p.is_file(): shutil.copy2(p,game/p.name)
    shutil.copytree(package/'Payload',game/'Payload')
    script=game/'manage.ps1'
    run('auto-locate extracted package',stdin='3\n',auto=True); installed(200)
    run('auto-locate restore',stdin='4\n',auto=True); assert not target.exists()
    assert sha(chinese)==manifest['base_chinese_sha256']
    assert before=={str(p):sha(p) for p in [real/'Inquisitor.exe',real/'03_zh.dat']}
    assert real_enhancements=={p.name:sha(p) for p in real.glob('04_enhancement*.dat')}
    assert not list((game/'Game').glob('*.tmp'))
    report=dict(checks=len(results),results=results,real_game_unchanged=True,chinese_localization_unchanged=True,shipped_zip_tested=True)
    (HERE/'installer_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))

if __name__ == '__main__':
    main()
