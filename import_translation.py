"""Remove AINiee header and validate complete protected token sequences.

No translation or automatic rewriting is performed. Writes official output only
after strict validation passes. Use --check on an existing headerless translation.
"""
import argparse
import csv
import json
import re
from pathlib import Path
from prepare_translation import ROOT, RULES


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    if any(len(row) != 1 for row in rows):
        raise ValueError('CSV 必须为单列；包含逗号与换行的文本须加 CSV 引号')
    return [row[0] for row in rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('translation', type=Path)
    parser.add_argument('--check', action='store_true', help='检查已经无表头的正式译文，不写文件')
    args = parser.parse_args()
    source = read(ROOT/'inquisitor_text.csv')
    target = read(args.translation)
    if not args.check:
        if not target or target[0] != 'source':
            raise ValueError('AINiee 输出首行必须是 source；无表头文件使用 --check')
        target = target[1:]
    if len(source) != len(target):
        raise ValueError(f'记录数量不一致：原文 {len(source)}，译文 {len(target)}')
    errors = []
    unchanged = 0
    for i, (s, t) in enumerate(zip(source, target), 1):
        reasons = []
        if not t.strip():
            reasons.append('空译文')
        for name, pattern in RULES:
            # Order matters for printf and repeated runtime variables.
            if re.findall(pattern, s) != re.findall(pattern, t):
                reasons.append(name)
        if s == t:
            unchanged += 1
        if reasons:
            errors.append(dict(row=i, reasons=reasons, source=s, translation=t))
    summary = dict(records=len(source), errors=len(errors), unchanged=unchanged, translation_completion_verified=False)
    (ROOT/'translation_validation.json').write_text(json.dumps(dict(summary=summary, issues=errors), ensure_ascii=False, indent=2), encoding='utf-8')
    print(summary)
    if errors:
        with (ROOT/'need_retranslate.csv').open('w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['行号', '原文', '当前译文', '问题'])
            for e in errors:
                w.writerow([e['row'], e['source'], e['translation'], '; '.join(e['reasons'])])
        return 1
    if not args.check:
        out = ROOT/'inquisitor_text_translated.csv'
        if out.exists():
            raise FileExistsError('正式译文已存在；先检查现有译文，避免覆盖')
        with out.open('w', encoding='utf-8-sig', newline='') as f:
            csv.writer(f, lineterminator='\n').writerows([t] for t in target)
        print('已导入正式译文；仍需检查未翻译行与译文质量。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
