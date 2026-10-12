"""Repair the reviewed AINiee export without rewriting its original file or cache."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'TranslateFiles' / 'repair_20261013_v2'
sys.path.insert(0, str(ROOT))
from prepare_translation import RULES


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.reader(handle))
    if any(len(row) != 1 for row in rows):
        raise ValueError('Expected single-column CSV')
    return [row[0] for row in rows]


def main():
    export = ROOT / 'inquisitor_ainiee_input_translated.csv'
    original_hash = hashlib.sha256(export.read_bytes()).hexdigest()
    if original_hash != '26ef825d7fdb88f0451cba666d8ab72dfdfb389f62ba81642d3c2e17cd3fc57a':
        raise ValueError('Export changed since review; review the new version first.')
    source = read(ROOT / 'inquisitor_text.csv')
    target = read(export)
    if target[0].lstrip('\ufeff') != 'source':
        raise ValueError('Unexpected header')
    target = target[1:]
    if len(source) != len(target):
        raise ValueError('Record counts differ')
    changes = []
    escape = re.compile(r'\\+[nrt]|\r\n|\r|\n')
    with (ROOT / 'TranslateFiles/validation_20261013/terminology_candidates.csv').open(encoding='utf-8-sig', newline='') as handle:
        candidates = list(csv.DictReader(handle))
    by_row = {}
    for item in candidates:
        by_row.setdefault(int(item['原文记录号']), []).append(item)

    for number, (s, old) in enumerate(zip(source, target), 1):
        t, reasons = old, []
        if any(re.findall(pattern, s) != re.findall(pattern, t) for _, pattern in RULES):
            a, b = escape.findall(s), escape.findall(t)
            if len(a) != len(b) or not a:
                raise ValueError(f'Cannot align escapes at {number}')
            def kind(token):
                return 'n' if token in ('\n', '\r', '\r\n') else token[-1]
            if list(map(kind, a)) != list(map(kind, b)):
                raise ValueError(f'Escape types differ at {number}')
            iterator = iter(a)
            t = escape.sub(lambda _: next(iterator), t)
            assert escape.sub('', old) == escape.sub('', t)
            reasons.append('按源文逐个恢复转义，保留全部正文及合法换行')

        def replace(before, after, why):
            nonlocal t
            if before in t:
                t = t.replace(before, after)
                reasons.append(why)

        if number == 23569:
            replace('New Save', '新建存档', '可见存档菜单漏译；保留尖括号转义')
        if number == 10607:
            replace('敲扎', '敲诈', 'extort 对应正文错字')
        # Guard each canonical component by the actual English entity in this record.
        components = {
            'Baphomet': [('巴弗灭', '巴风特'), ('巴弗默', '巴风特')],
            'Orthenius': [('奥尔特尼乌斯', '奥塞尼乌斯')],
            'Ventimus': [(name, '文蒂穆斯') for name in ['文提穆斯', '文蒂姆斯', '文提慕斯', '文图穆斯', '文提姆斯']],
            'Truncquillius': [('特隆奎利乌斯', '特伦奎利乌斯')],
            'Weintraum': [('魏因特拉姆', '温特劳姆')],
            'Alvaron': [('阿尔瓦伦', '阿尔瓦隆')],
            'seneschal': [('家宰', '总管'), ('管家', '总管')],
            'Dark prophet': [('暗黑先知', '黑暗先知')],
            'Archangel Gabriel': [('天使长加百列', '大天使加百列')],
        }
        for name, edits in components.items():
            if re.search(r'(?<![A-Za-z])' + re.escape(name) + r'(?![A-Za-z])', s, re.I):
                for before, after in edits:
                    replace(before, after, '按已冻结名称统一 ' + name)
        for item in by_row.get(number, []):
            name = item['术语原文']
            edits = {
                'Giant bat': [('巨蝙蝠', '巨型蝙蝠')],
                'Priest Romius': [('罗米乌斯牧师', '罗米乌斯神父'), ('牧师罗米乌斯', '罗米乌斯神父')],
                'priest Gilbert': [('牧师吉尔伯特', '吉尔伯特神父')],
                'Ludwig Weintraum': [('温特劳姆（路德维希）', '路德维希·温特劳姆')],
                'school of Severinus': [('塞维里努斯学派', '塞维里努斯法学流派')],
                'Devil\'s Root': [('魔鬼之根', '恶魔之根')],
                'Dark High Priest': [('黑暗高阶牧师', '黑暗大祭司'), ('黑暗大牧师', '黑暗大祭司'),
                                     ('高阶牧师', '大祭司'), ('大牧师', '大祭司')],
                'Magister of the Chapter': [('正义兄弟会分会的本地最高导师', '正义兄弟会本地分会会长'),
                                           ('正义兄弟会分会的本地大师', '正义兄弟会本地分会会长'),
                                           ('正义兄弟会分会的教务长', '正义兄弟会分会会长')],
                'The Holy Grave': [('先知圣墓', '第一先知的圣墓')],
            }.get(name, [])
            for before, after in edits:
                replace(before, after, '候选语境复核后统一 ' + name)
            if name == 'Ludwig Weintraum' and '路德维希·温特劳姆' not in t:
                replace('温特劳姆', '路德维希·温特劳姆', '补回源文完整人物姓名')
        if number == 5841:
            replace('所幸的是，新秩序之子教团', '对乌尔瑟斯特而言，所幸的是，新秩序之子教团', '保留原文明确国名 Ultherst')
        if number == 12119:
            replace('路易斯王储', '路易王储', '统一 Louis 核心译名，保留 Crown Prince 王储身份')
        if number == 22803:
            replace('"审判官"圣物', '"审判者"圣物', '此处为圣物专名，区分职业审判官')
            replace('审判官圣物', '审判者圣物', '此处为圣物专名，区分职业审判官')
        if t != old:
            changes.append(dict(row=number, source=s, before=old, after=t, reasons=reasons))
        target[number-1] = t
    errors = []
    for number, (s, t) in enumerate(zip(source, target), 1):
        if not t.strip():
            errors.append(dict(row=number, reason='Empty translation'))
        for name, pattern in RULES:
            if re.findall(pattern, s) != re.findall(pattern, t):
                errors.append(dict(row=number, reason=name))
    if errors:
        raise ValueError(str(errors))
    assert hashlib.sha256(export.read_bytes()).hexdigest() == original_hash
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = OUT / 'inquisitor_text_repaired.csv'
    if candidate.exists():
        raise FileExistsError('Repair output already exists; do not overwrite reviewed work.')
    with candidate.open('w', encoding='utf-8-sig', newline='') as handle:
        csv.writer(handle, lineterminator='\n').writerows([text] for text in target)
    write = lambda path, data: path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    write(OUT / 'repair_changes.json', dict(input_sha256=original_hash, changes=changes))
    write(OUT / 'strict_validation.json', dict(records=len(source), errors=errors,
                                             changed_rows=len(changes), original_unchanged=True,
                                             repaired_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest()))
    decisions = []
    for item in candidates:
        number = int(item['原文记录号'])
        expected = item['冻结译名']
        # Semantic exceptions are explicitly decided, rather than reported as unresolved errors.
        if expected in target[number-1]:
            verdict, reason = 'resolved', '修复后匹配冻结译名'
        elif item['术语原文'] in {'Ring', 'Health', 'Possession', 'Stranger', 'Initiate', 'Thieving', 'Cursed Paladin',
                                  'Ethel', 'Sanctus', 'Mortis', 'Strength', 'Intelligence', 'Fear', 'the Crown', 'The Realm', 'Inquisitor'}:
            verdict, reason = 'accepted_context', '普通词/词性或语境、虚构语及网址匹配；不强套专名或属性译名'
        elif item['术语原文'] in {
            'Hillbrandt Chapter', 'Alvaron Chapter', 'Order of the Brotherhood', "Truthorn's tavern",
            'Rite of Summoning', 'Elenian runic alphabet', 'Elenian civilization', 'Erebornian lawyers',
            'monstrance of Saint Rhodrick', 'diocesan bishop',
        }:
            verdict, reason = 'accepted_expression', '名称/组织/地点/身份均保留，中文属格、词序或修饰成分使连续字面匹配失败'
        elif item['术语原文'] == 'The Holy Grave':
            verdict, reason = 'accepted_expression', '保留圣墓自然称呼及第一先知核心姓名；不强加圣地墓穴的字面译法'
        elif item['术语原文'] == 'Scamp':
            verdict, reason = 'accepted_context', '形容孩子的普通名词捣蛋鬼/调皮鬼，不是名为斯坎普的实体'
        elif item['术语原文'] == 'prince Louis':
            verdict, reason = 'accepted_context', '源文同时为 Crown Prince；保留王储而非泛化王子，Louis 核心译名已统一'
        elif item['术语原文'] == 'the Citadel':
            verdict, reason = 'accepted_expression', '正义兄弟会城堡已明确所在要塞，不强行堆叠城堡要塞'
        elif item['术语原文'] == 'Lord God':
            verdict, reason = 'accepted_expression', '保留我主/主的恩典等原句宗教表达，不机械插入主上帝'
        elif item['术语原文'] == 'nephrite statuette':
            verdict, reason = 'accepted_expression', '软玉制成的雕像明确保留材质与物品，不将宽泛材质强行收窄为碧玉'
        elif item['术语原文'] == 'King Rafmaanii the Wise':
            verdict, reason = 'accepted_expression', '明君拉夫马尼王表达国王的睿智称号，名字一致'
        else:
            verdict, reason = 'review_required', '词序、自然表达或专名需逐项记录语义结论'
        decisions.append(dict(row=number, term=item['术语原文'], expected=expected, verdict=verdict,
                              reason=reason, source=item['原文'], translation=target[number-1]))
    write(OUT / 'terminology_review.json', decisions)
    print('Repaired records:', len(target), 'changed rows:', len(changes), 'strict errors:', len(errors))


if __name__ == '__main__':
    main()
