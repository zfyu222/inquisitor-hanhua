"""Build a separate DRPK localization overlay, with exact spans and bitmap fonts.

Does not write to the installed game. All resource bytes are verified after unpack.
Requires Pillow and fontTools for the font atlas; drpk_extract.py for SFL validation.
"""
import csv
import ctypes
import functools
import hashlib
import io
import json
import re
import struct
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from drpk_extract import entries, expand

ROOT = Path(__file__).resolve().parent
WORK = ROOT / 'Repack'
XOR = bytes(x ^ 0x4a for x in range(256))
FONT = Path('C:/Windows/Fonts/simhei.ttf')
GLYPH = re.compile(r"Character='(.)' (.*)")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        data = list(csv.reader(f))
    assert all(len(row) == 1 for row in data)
    return [row[0] for row in data]

def load_fonts():
    result = {}
    cache = WORK / 'font_original'
    manifest_path = cache / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for archive in ['01_local', '02_patch']:
            for filename, expected in manifest.items():
                if filename.startswith(archive+'_'):
                    content = (cache/filename).read_bytes()
                    assert sha(content) == expected, filename
                    result['local/fnt/'+filename[len(archive)+1:]] = content
        return result
    for archive in ['01_local.dat', '02_patch.dat']:
        for name, size, packed, offset, content in entries(ROOT / 'Game/Game' / archive):
            if name.lower().startswith('local/fnt/'):
                result[name] = expand(content, size)
    return result

def make_fonts(characters):
    original = load_fonts()
    cmap = TTFont(str(FONT)).getBestCmap()
    result = {}
    report = []
    for name, size, height in [('Nosferatu', 16, 26), ('NosferatuS', 12, 20), ('NosferatuSBlack', 12, 20)]:
        bfi = original[f'local/fnt/{name}.bfi'].decode('utf-16')
        bitmap_name = 'NosferatuS' if name == 'NosferatuSBlack' else name
        bitmap = Image.open(io.BytesIO(original[f'local/fnt/{bitmap_name}.bmp'])).convert('RGB')
        oldw, oldh = bitmap.size
        atlas = Image.new('RGB', (2048, 2048), 'black')
        atlas.paste(bitmap, (0, 0))
        existing = set()
        lines = []
        for line in bfi.splitlines():
            if not line:
                continue
            match = GLYPH.fullmatch(line)
            if match:
                existing.add(match[1])
                for field, factor in [('u1', oldw / 2048), ('u2', oldw / 2048), ('v1', oldh / 2048), ('v2', oldh / 2048)]:
                    line = re.sub(rf'\b{field}=([0-9.]+)', lambda m: f'{field}={float(m[1])*factor:.10f}', line)
            lines.append(line)
        missing = sorted(characters - existing - set('\r\n\t'), key=ord)
        unsupported = [char for char in missing if ord(char) not in cmap]
        assert not unsupported, f'Font coverage missing: {unsupported!r}'
        font = ImageFont.truetype(str(FONT), size)
        draw = ImageDraw.Draw(atlas)
        cellw = size + 4
        columns = 2048 // cellw
        assert oldh + ((len(missing) + columns - 1) // columns)*height <= 2048
        for index, char in enumerate(missing):
            x = (index % columns)*cellw
            y = oldh + (index // columns)*height
            advance = max(1, round(font.getlength(char)))
            # A two-pixel border protects sampling; preserve the existing line height.
            draw.text((x+2, y+3), char, font=font, fill='white', anchor='lt')
            lines.append(f"Character='{char}' u1={x/2048:.10f} v1={y/2048:.10f} u2={(x+cellw)/2048:.10f} v2={(y+height)/2048:.10f} WidthA=0 WidthB={advance} WidthC=1 ScreenRectLeft=-2 ScreenRectTop=0 ScreenRectRight={cellw-2} ScreenRectBottom={height} CharAscent=0")
        result[f'local/fnt/{name}.bfi'] = ('\r\n'.join(lines)+'\r\n').encode('utf-16')
        assert all(c in existing or c in missing or c in '\r\n\t' for c in characters)
        if name != 'NosferatuSBlack':
            buffer = io.BytesIO()
            atlas.save(buffer, format='BMP')
            result[f'local/fnt/{name}.bmp'] = buffer.getvalue()
            # A small generated sample for visual QA outside the game.
            preview = Image.new('RGB', (600, height*3), 'black')
            ImageDraw.Draw(preview).text((4, 4), '审判官：新游戏、读取存档、设置、退出\n艾尔达、圣堂武士、生命值、魔法值', font=font, fill='white')
            preview.save(WORK / f'font_preview_{name}.png')
        report.append(dict(font=name, original_glyphs=len(existing), added_glyphs=len(missing), atlas=[2048,2048], point_size=size))
    return result, report

def pack(resources, path):
    # The last entry word is the FIRST SFL block length, not a checksum.
    # The last footer word is the maximum expanded resource size.
    data = bytearray(b'DRPK\0\0'.translate(XOR))
    records = bytearray()
    dirs, names = bytearray(), bytearray()
    dir_offsets = {}
    # IDA 0x406FA7: CompareStringA(0x409, NORM_IGNORECASE, ..., -1, ..., -1).
    # Locale ordering differs from ASCII sorting for underscores/digits.
    compare = ctypes.windll.kernel32.CompareStringA
    compare.argtypes = [ctypes.c_uint, ctypes.c_ulong, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    def order(left, right):
        for a, b in zip(left.rsplit('/',1), right.rsplit('/',1)):
            value = compare(0x409,1,a.replace('/','\\').encode('cp1252'),-1,b.replace('/','\\').encode('cp1252'),-1)
            assert value in [1,2,3]
            if value != 2:
                return value-2
        return 0
    ordered = sorted(resources, key=functools.cmp_to_key(order))
    assert all(order(a,b) < 0 for a,b in zip(ordered, ordered[1:]))
    for name in ordered:
        content = resources[name]
        directory, filename = name.rsplit('/', 1)
        directory = directory.replace('/', '\\')
        if directory not in dir_offsets:
            dir_offsets[directory] = len(dirs)
            dirs.extend(directory.encode('cp1252')+b'\0')
        name_offset = len(names)
        names.extend(filename.encode('cp1252')+b'\0')
        packed = bytearray()
        for start in range(0, len(content), 16384):
            chunk = content[start:start+16384]
            packed.extend(struct.pack('<H', len(chunk)+1)+b'\x80'+chunk)
        assert content
        offset = len(data)
        data.extend(packed)
        records.extend(struct.pack('<6I', dir_offsets[directory], name_offset, len(content), len(packed), offset, int.from_bytes(packed[:2], 'little')))
    data.extend(records)
    data.extend(dirs)
    data.extend(names)
    data.extend(struct.pack('<4I', len(resources), len(dirs), len(names), max(map(len, resources.values()))))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.translate(XOR))
    found = {}
    for name, size, packed, offset, content in entries(path):
        actual = expand(content, size)
        assert actual == resources[name], name
        found[name] = sha(actual)
    assert set(found) == set(resources)
    return found

def main():
    WORK.mkdir(exist_ok=True)
    source = rows(ROOT / 'inquisitor_text.csv')
    target = rows(ROOT / 'inquisitor_text_translated.csv')
    assert len(source) == len(target) == 24074
    locations = [json.loads(line) for line in (ROOT/'text_locations.jsonl').read_text(encoding='utf-8').splitlines()]
    originals = json.loads((ROOT/'extraction_report.json').read_text(encoding='utf-8'))['source_files']
    expected_hashes = {(row['archive'], row['file']): row['sha256'] for row in originals}
    grouped = defaultdict(list)
    for row in locations:
        grouped[(row['archive'], row['file'])].append(row)
    resources, deferred = {}, []
    count = 0
    for (archive, filename), group in grouped.items():
        raw = (ROOT/'extracted'/archive[:-4]/filename).read_bytes()
        assert sha(raw) == expected_hashes[(archive, filename)]
        text = raw.decode('utf-16')
        for row in sorted(group, key=lambda row: row['start'], reverse=True):
            index = row['row']-1
            assert text[row['start']:row['end']] == source[index]
            # IDA: 0x4B0D0D copies NPCName into the UTF-16 display buffer;
            # 0x4B3155 uses it as the speaker prefix of visible dialogue text.
            # Lookup IDs and action expressions remain outside the extracted spans.
            text = text[:row['start']] + target[index] + text[row['end']:]
            count += 1
        resources[filename] = text.encode('utf-16')
    characters = set(''.join(target))
    fonts, font_report = make_fonts(characters)
    resources.update(fonts)
    output = WORK/'Files/Game/03_zh.dat'
    hashes = pack(resources, output)
    report = dict(overlay=str(output), overlay_sha256=sha(output.read_bytes()), overlay_bytes=output.stat().st_size,
                  translated_locations=count, resources=len(resources), roundtrip_verified=len(hashes),
                  fonts=font_report, deferred_npcname=deferred, resource_sha256=hashes,
                  source_csv_sha256=sha((ROOT/'inquisitor_text.csv').read_bytes()),
                  target_csv_sha256=sha((ROOT/'inquisitor_text_translated.csv').read_bytes()),
                  game_verification='Pending: this script does not deploy or launch the game.')
    (WORK/'build_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key not in ['resource_sha256','deferred_npcname']}, ensure_ascii=False, indent=2))
    print('Deferred NPCName:', len(deferred))

if __name__ == '__main__':
    main()
