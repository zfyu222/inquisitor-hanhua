"""Build a font-only overlay from the verified Chinese v1.0 payload. No deployment."""
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(PROJECT))
from build_patch import pack
from drpk_extract import entries, expand
from PIL import Image, ImageDraw, ImageFont

BASE_SHA = '3164493a2bb1ce571709d86f3fc438c61ec47b06629436fc90851f448b55b2e2'
EXE_SHA = '88854166fe459cb1937b075604d906c88c3e1109d7b87fb17cb494939c7a9276'
NAMES = ['Nosferatu', 'NosferatuS', 'NosferatuSBlack']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def preview(fonts, scaled):
    """Illustrative BFI layout simulation, not an in-game screenshot."""
    canvas = Image.new('RGB', (1100, 400), '#202020')
    draw = ImageDraw.Draw(canvas)
    label = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 18)
    draw.text((12, 8), '离线字体预览（非游戏截图）    左：100%    右：125%', font=label, fill='white')
    sample = '审判官：生命值、魔法值，天地一二三。\n任务日志——新的旅程……ABC 012345'
    for row, name in enumerate(NAMES):
        for col, source in enumerate([fonts, scaled]):
            bfi = source[f'local/fnt/{name}.bfi'].decode('utf-16')
            sx = float(re.search(r'^TextScaleX=(.*)$', bfi, re.M)[1])
            sy = float(re.search(r'^TextScaleY=(.*)$', bfi, re.M)[1])
            gap = int(re.search(r'^LineGap=(.*)$', bfi, re.M)[1]) * sy
            bitmap = 'NosferatuS' if name == 'NosferatuSBlack' else name
            atlas = Image.open(io.BytesIO(fonts[f'local/fnt/{bitmap}.bmp'])).convert('RGB')
            glyphs = {line[11]: dict((k,float(v)) for k,v in re.findall(r'(\w+)=(-?[0-9.]+)', line))
                      for line in bfi.splitlines() if line.startswith('Character=')}
            origin = 12 + col*550
            top = 45 + row*115
            draw.text((origin, top), name, font=label, fill='#cccccc')
            x, y = float(origin+4), float(top+24)
            for char in sample:
                if char == '\n':
                    x, y = float(origin+4), y+gap
                    continue
                f = glyphs[char]
                box = tuple(round(f[k]*dim) for k,dim in [('u1',atlas.width),('v1',atlas.height),('u2',atlas.width),('v2',atlas.height)])
                image = atlas.crop(box)
                w = max(1, round((f['ScreenRectRight']-f['ScreenRectLeft'])*sx))
                h = max(1, round((f['ScreenRectBottom']-f['ScreenRectTop'])*sy))
                image = image.resize((w,h), Image.Resampling.BILINEAR)
                canvas.paste(image, (round(x+f['ScreenRectLeft']*sx),round(y+f['ScreenRectTop']*sy)))
                x += (f['WidthA']+f['WidthB']+f['WidthC'])*sx
    canvas.save(HERE/'preview.png')

def main():
    candidates = [PROJECT/'Dispatch/Files/Game/03_zh.dat', PROJECT/'Repack/Files/Game/03_zh.dat']
    base = next((p for p in candidates if p.exists() and sha(p.read_bytes()) == BASE_SHA), None)
    if base is None:
        raise SystemExit('Verified Chinese v1.0 payload not found; refusing to build from another version.')
    fonts = {name:expand(data,size) for name,size,_,_,data in entries(base) if name.startswith('local/fnt/')}
    assert set(fonts) == {f'local/fnt/{n}.bfi' for n in NAMES} | {'local/fnt/Nosferatu.bmp','local/fnt/NosferatuS.bmp'}
    scaled, counts = {}, {}
    for name in NAMES:
        path = f'local/fnt/{name}.bfi'
        before = fonts[path].decode('utf-16')
        after = before
        for axis in ['X', 'Y']:
            pattern = rf'(?m)^TextScale{axis}=1\.0(?=\r?$)'
            after, n = re.subn(pattern, f'TextScale{axis}=1.25', after)
            assert n == 1, (path, axis, n)
        # Every other byte/field, including UVs, bearings, line gap and all glyphs, is preserved.
        assert after.replace('TextScaleX=1.25','TextScaleX=1.0').replace('TextScaleY=1.25','TextScaleY=1.0') == before
        scaled[path] = after.encode('utf-16')
        counts[name] = before.count('\nCharacter=')
    output = HERE/'Files/Game/04_enhancement_font125.dat'
    hashes = pack(scaled, output)
    # Cross-check using an independent decoder.
    workspace = PROJECT.parents[1]
    check = HERE/'verification/quickbms'
    check.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(workspace/'Tools/QuickBMS/quickbms.exe'), '-o',
                             str(workspace/'Tools/QuickBMS/inquisitor.bms'), str(output), str(check)],
                            capture_output=True)
    (HERE/'verification/quickbms.log').write_bytes(result.stdout+result.stderr)
    assert result.returncode == 0, result.returncode
    assert {p.relative_to(check).as_posix() for p in check.rglob('*') if p.is_file()} == set(scaled)
    for name, content in scaled.items():
        assert (check/name).read_bytes() == content, name
    report = dict(feature='font_scale_125', scale_x=1.25, scale_y=1.25,
                  base_chinese_sha256=BASE_SHA, supported_exe_sha256=EXE_SHA,
                  payload='Game/'+output.name, payload_sha256=sha(output.read_bytes()),
                  payload_bytes=output.stat().st_size, resources=hashes, glyph_counts=counts,
                  changed_fields=['TextScaleX: 1.0 -> 1.25', 'TextScaleY: 1.0 -> 1.25'],
                  roundtrip_verified=3, independent_quickbms_verified=3,
                  runtime_verification='pending; offline build only',
                  scope='BFI-rendered text; menu text baked into images is outside this feature')
    (HERE/'build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest = dict(report)
    manifest['version'] = '1.0-local'
    (HERE/'Files/PATCH_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    preview(fonts, scaled)
    files = sorted(p for p in (HERE/'Files').rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    (HERE/'Files/SHA256SUMS.txt').write_text(''.join(f'{sha(p.read_bytes())}  {p.relative_to(HERE/"Files").as_posix()}\n' for p in files),encoding='utf-8')
    archive = HERE/'Inquisitor_独立增强补丁_字体125.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted((HERE/'Files').rglob('*')):
            if p.is_file():
                z.write(p,p.relative_to(HERE/'Files').as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert z.read(report['payload']) == output.read_bytes()
    print(json.dumps(dict(report, zip_bytes=archive.stat().st_size, zip_sha256=sha(archive.read_bytes())),ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
