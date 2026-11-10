"""Build selectable font overlays; never deploy into the actual game."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT))
from build_patch import pack
from drpk_extract import entries, expand

BASE_SHA = '3164493a2bb1ce571709d86f3fc438c61ec47b06629436fc90851f448b55b2e2'
EXE_SHA = '88854166fe459cb1937b075604d906c88c3e1109d7b87fb17cb494939c7a9276'
LEGACY_SHA = '028a5b7b718dfa9debe264d1349ceee1aab492e547edcacba05ca50301776a2f'
NAMES = ['Nosferatu', 'NosferatuS', 'NosferatuSBlack']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    candidates = [PROJECT/'Dispatch/Files/Game/03_zh.dat', PROJECT/'Repack/Files/Game/03_zh.dat']
    base = next((p for p in candidates if p.exists() and sha(p.read_bytes()) == BASE_SHA), None)
    if base is None:
        raise SystemExit('Verified Chinese v1.0 payload not found.')
    fonts = {n:expand(d,s) for n,s,_,_,d in entries(base) if n.startswith('local/fnt/')}
    options = []
    for percent in [125,150,200]:
        factor = str(percent/100)
        scaled = {}
        for name in NAMES:
            path = f'local/fnt/{name}.bfi'
            before = fonts[path].decode('utf-16')
            after = before
            for axis in ['X','Y']:
                after,n = re.subn(rf'(?m)^TextScale{axis}=1\.0(?=\r?$)', f'TextScale{axis}={factor}',after)
                assert n == 1
            assert after.replace('TextScaleX='+factor,'TextScaleX=1.0').replace('TextScaleY='+factor,'TextScaleY=1.0') == before
            scaled[path] = after.encode('utf-16')
        payload = HERE/f'Files/Payload/font{percent}.bin'
        hashes = pack(scaled,payload)
        (HERE/'verification').mkdir(exist_ok=True)
        check = Path(tempfile.mkdtemp(prefix=f'quickbms{percent}_',dir=HERE/'verification'))
        workspace = PROJECT.parents[1]
        r = subprocess.run([str(workspace/'Tools/QuickBMS/quickbms.exe'),'-o',str(workspace/'Tools/QuickBMS/inquisitor.bms'),str(payload),str(check)],capture_output=True)
        (check.parent/f'quickbms{percent}.log').write_bytes(r.stdout+r.stderr)
        assert r.returncode == 0
        assert {p.relative_to(check).as_posix() for p in check.rglob('*') if p.is_file()} == set(scaled)
        assert all((check/n).read_bytes() == d for n,d in scaled.items())
        options.append(dict(percent=percent,scale=percent/100,payload=f'Payload/font{percent}.bin',sha256=sha(payload.read_bytes()),bytes=payload.stat().st_size,resources=hashes,roundtrip_verified=3,quickbms_verified=3))
    manifest = dict(version='1.1-local',feature='selectable_font_scale',supported_exe_sha256=EXE_SHA,
                    base_chinese_sha256=BASE_SHA,target='Game/04_enhancement_font.dat',
                    legacy_target='Game/04_enhancement_font125.dat',legacy_sha256=LEGACY_SHA,options=options)
    (HERE/'Files/PATCH_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report = dict(manifest,runtime_verification='pending; offline only',changed_fields=['TextScaleX','TextScaleY'])
    (HERE/'build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Windows PowerShell 5.1 needs a BOM for Chinese prompts.
    script = HERE/'Files/manage.ps1'
    script.write_text(script.read_text(encoding='utf-8-sig'),encoding='utf-8-sig')
    for p in (HERE/'Files').glob('*.cmd'):
        p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
    files = sorted(p for p in (HERE/'Files').rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (HERE/'Files/SHA256SUMS.txt').write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(HERE/"Files").as_posix()}\n' for p in files),encoding='utf-8')
    archive = HERE/'Inquisitor_独立增强补丁_字体可选.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted((HERE/'Files').rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(HERE/'Files').as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            expected,name = line.split('  ',1)
            assert sha(z.read(name)) == expected
    summary = dict(zip=archive.name,bytes=archive.stat().st_size,sha256=sha(archive.read_bytes()),scales=[125,150,200],zip_and_checksums='passed',runtime_verification='pending')
    (HERE/'package_verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
