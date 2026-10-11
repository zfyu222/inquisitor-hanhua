"""Create one exact-text corpus and reversible character-span location map."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = ['01_local', '01_data', '02_patch']
TAG = re.compile(r'<(?P<tag>string|visname|desc|text|title|NPCName)\b(?P<attrs>[^>]*)>(?P<value>.*?)</(?P=tag)>', re.S | re.I)


def main():
    effective = {}
    overridden = 0
    for archive in ORDER:
        for p in sorted((ROOT/'extracted'/archive).rglob('*')):
            if not p.is_file() or p.name == 'archive_manifest.json':
                continue
            name = p.relative_to(ROOT/'extracted'/archive).as_posix()
            if name.lower() in effective:
                overridden += 1
            effective[name.lower()] = (archive, name, p)
    texts = []
    indices = {}
    locations = []
    skipped = []
    files = []
    counts = Counter()
    for archive, name, path in sorted(effective.values(), key=lambda x: x[1].lower()):
        suffix = path.suffix.lower()
        if not name.lower().startswith('local/') or suffix not in {'.txt', '.dlt', '.dlg'}:
            continue
        raw = path.read_bytes()
        assert raw.startswith(b'\xff\xfe'), name
        s = raw.decode('utf-16')
        # Mask full-line developer comments without changing span offsets.
        masked = re.sub(r'(?m)^[ \t]*#[^\r\n]*', lambda m: ' '*len(m[0]), s)
        found = 0
        for m in TAG.finditer(masked):
            tag = m['tag'].lower()
            if suffix == '.dlg' and tag != 'npcname':
                continue
            value = s[m.start('value'):m.end('value')]
            record_id = re.search(r'\bid="([^"]*)"', m['attrs'])
            record_id = record_id[1] if record_id else None
            if not value.strip() or record_id == 'CharConvert' or not re.search(r'[A-Za-zÀ-ž]', value):
                skipped.append(dict(file=name, tag=tag, id=record_id, value=value, reason='empty/numeric/punctuation/CharConvert'))
                continue
            if value not in indices:
                indices[value] = len(texts)+1
                texts.append(value)
            row = indices[value]
            locations.append(dict(row=row, archive=archive+'.dat', file=name, tag=tag, id=record_id,
                                  start=m.start('value'), end=m.end('value'),
                                  classification='display_name_review_lookup' if tag=='npcname' else 'display_text'))
            found += 1
            counts[tag] += 1
        # Assert that all DLT string openings have corresponding closing tags.
        if suffix == '.dlt':
            assert len(re.findall(r'<string\b', masked, re.I)) == len(list(TAG.finditer(masked))), name
        files.append(dict(archive=archive+'.dat', file=name, sha256=hashlib.sha256(raw).hexdigest(), locations=found))
    with (ROOT/'inquisitor_text.csv').open('w', encoding='utf-8-sig', newline='') as f:
        csv.writer(f, lineterminator='\n').writerows([t] for t in texts)
    # Local AINiee requires a header; keep the official corpus headerless.
    with (ROOT/'inquisitor_ainiee_input.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['source'])
        w.writerows([t] for t in texts)
    with (ROOT/'text_locations.jsonl').open('w', encoding='utf-8') as f:
        for row in locations:
            f.write(json.dumps(row, ensure_ascii=False)+'\n')
    report = dict(unique_texts=len(texts), locations=len(locations), files=len(files),
                  overridden_extracted_files=overridden, tags=dict(counts),
                  characters=sum(map(len,texts)), multiline_records=sum('\n' in t or '\r' in t for t in texts),
                  skipped=skipped, source_files=files,
                  priority='02_patch supersedes same paths in 01_local/01_data; verify runtime priority when repacking')
    (ROOT/'extraction_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    # Verify every emitted row maps back exactly to the untouched resource content.
    rows = list(csv.reader((ROOT/'inquisitor_text.csv').open(encoding='utf-8-sig', newline='')))
    assert all(len(r)==1 for r in rows) and len(rows)==len(texts)
    cache = {}
    for loc in locations:
        key=(loc['archive'][:-4],loc['file'])
        if key not in cache:
            cache[key]=(ROOT/'extracted'/key[0]/key[1]).read_bytes().decode('utf-16')
        assert cache[key][loc['start']:loc['end']] == rows[loc['row']-1][0]
    print({k:v for k,v in report.items() if k not in {'skipped','source_files'}})


if __name__ == '__main__':
    main()
