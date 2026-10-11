"""Build reviewed project tables and an evidence-backed change log.

Reads only the frozen analysis snapshot and source corpus. Does not write live
AINiee state. Manual corrections are deliberately limited to supported findings.
"""
import copy
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C_FIX = {
    0: ('信仰捍卫者金典', '物品', '原文第22198条明确说明是 Directorium Inquisitorum 的别称，非汤姆'),
    1: ('道恩·冯·布卢滕里希男爵庄园', '地名', 'Mansion 是庄园，原文6175等描述庄园诅咒'),
    14: ('论撒旦及其他地狱仆从的召唤', '物品', '完整 source 是书名，不能仅译为撒旦'),
    15: ('大天使加百列骑士团印戒', '物品', '完整 source 是印戒，非天使本体'),
    40: ('阿尔萨蒙古教团', '组织', '原文14586等明确指古老教团，非阿尔萨蒙本体'),
    41: ('弗雷德里克神父的日记', '物品', '日记条目不能用作者名字替代'),
    53: ('圣以西结启示录', '物品', '原文4853指圣典中的启示篇章，非人物'),
    54: ('圣努斯米尔修道院', '地名', '原文15792描述收留并照料人物的修道院'),
    55: ('冯·洪特男爵的棺木', '物品', '棺木与人物分开'),
    67: ('布拉汉的银护符', '物品', '完整物品名，不能省略护符'),
    71: ('圣伯特霍尔德之夜', '其他', '原文3335等指历史事件'),
    139: ('神秘之声', '其他', '泛指声音，缺少确定人物实体，移至术语'),
    237: ('扎尔格领主的心脏', '物品', '原文22530为完整物品名'),
    239: ('恩·莱尼乌斯的护符', '物品', '完整物品名，非失主本体'),
    266: ('古布林的首级', '物品', '首级战利品与人物分开'),
    369: ('爱德华国王', None, '原文18151等明确是颁布禁赌法令的国王；Kind 为原文错拼，非人名金'),
    375: ('戈耳工', '种族', '原文23672描述一类神话生物'),
    377: ('别西卜', '其他', '原文1144、4348用复数作恶魔/恶人称呼，不指定为单一人物或独立种族'),
    403: ('草药师', '身份', '原文23980泛指可制作灵药的草药师，非专名NPC'),
    540: ('灯神', '种族', '复数生物，非专名NPC'),
    554: ('盗贼', '身份', '职业名而非人物专名'),
    562: ('圣以西结启示录', '物品', '启示篇章与作者分开'),
    364: ('阿尔瓦·弗洛克', None, '补全 Flock 姓氏，source 为完整人物名'),
    192: ('魅魔瑟尔迪', None, '完整 source 含 Succubus 身份称谓'),
    360: ('受诅咒的琼', None, '完整 source 含 Cursed 修饰词'),
    211: ('朗哈姆的阿布拉姆公爵', None, '补全原文地域称谓 of Longham'),
    2: ('奇迹者阿尔莫德二世教皇', None, '补全原文教皇及奇迹者称号'),
    26: ('德·马拉梅特大团长', None, '与完整姓名 Christoffer de Malamert 统一姓氏'),
    91: ('埃蒂安·德·帕斯克骑士', None, '同一NPC的名字写法统一'),
    119: ('草药师恩丽·容维特', None, 'Wise Woman 在游戏中为草药师身份，与名字别称统一'),
    58: ('草药师恩丽·容维特', None, 'Wisewoman 与 Herbwomen 的游戏语境一致'),
    148: ('艾莉西亚·维尔滕罗特', None, '同一草药师的 Elisia/Ellisa/Ellisia 拼写变体统一'),
    149: ('艾莉西亚·维尔滕罗特', None, '同一草药师的拼写变体统一'),
    247: ('里耶凡·达尔德里奥', None, '与资源显示名 Rieven d\'Ardrieaux 统一'),
    296: ('园丁道奈', None, '与 Downay the Gardener 统一'),
    309: ('苏珊·布劳赫纳', None, '与 Suzan Brauchner 同一商贩统一'),
    346: ('让·德·吉斯', None, '与 Jean de Guise 资源显示名及称谓条目统一'),
    374: ('维克·伦斯', None, '同一名字 Length/Lenght 拼写变体统一'),
    412: ('埃蒂安·帕斯克', None, '与 de Pasque 姓名核心统一'),
    518: ('赞·德雷姆', None, '与 Zan\'Drem/Zan Drem 核心译名统一'),
    347: ('马尔修斯神父', None, '与 Father/Brother Marcius 名字核心统一'),
    218: ('赫尔夫·雷赫茨维瑟', None, '与 Hulph Rechtzwurther 的重音符号变体统一'),
    228: ('亨利·德·蒙特罗', None, '与 Henry de Montreaux 的名字变体统一'),
}
T_FIX = {
    37: ('正义兄弟会分会', '组织', 'chapter 是骑士团地方分会，与教区 diocese 区分'),
    76: ('圣务院法官', '身份', '与 Holy Office 核心译名统一，保留法官称谓'),
    46: ('法力恢复药水', '物品', 'Mana 与项目术语法力统一'),
    82: ('圣罗德里克圣体光', '物品', '保留正确祭具名称圣体光；统一其他 monstrance 条目的误译'),
    95: ('圣罗德里克圣体光', '物品', '同一圣物的 Rhodrick/Rhodric 写法统一'),
    99: ('圣务院裁判庭', '组织', '不能省略 Curia 裁判庭层级'),
    109: ('修会大团长', '身份', 'Grand Master 在骑士团语境与大团长统一'),
    209: ('异教之夜教团', '组织', '与 Cult of the Pagan Night 统一'),
    218: ('宗教裁判所最高审判庭', '组织', '与带 the 的同一机构名称统一'),
    266: ('本修会项链', '物品', 'my Order 保留指代，不能凭短词直接写成兄弟会'),
    270: ('亡者之死', '技能', 'Death 与 Dance 是不同词，原文无命中，隔离；此建议不进入启用表'),
    295: ('乌尔瑟斯特王国', '地名', 'Realm/Kingdom 在本作指同一王国'),
    303: ('特鲁索恩酒馆', '地名', 'Truthorn 是人名，不能把姓氏字面译为真角'),
    315: ('厄斯特威克佣兵', '组织', '译名中遗留英文地名，统一 Erstwick 音译'),
    323: ('厄斯特威克之刺', '物品', '译名中遗留英文地名'),
    338: ('hellixarum devilicum', '技能', '虚构拉丁式名称缺少足以确定恶魔之舞含义的证据，暂保留原名'),
    343: ('很好，我的孩子！', '其他', '译名字段不能夹带原文和解释括注，备注另存'),
    370: ('山地巨魔', '种族', '与 Mountain Troll 一致，保留 mountain 修饰'),
    378: ('圣贝塞斯达修会', '组织', '与 Order of Saint Bethesda 统一'),
    383: ('冯·洪特庄园', '地名', '与 von Hunth 姓氏统一'),
    419: ('神罚灾难', '其他', 'source 混入中文注释，改回 Scourges of God；语境为饥荒、瘟疫、火雨'),
    421: ('死灵之书', '物品', 'Libre 在此为书名构成，不能译作自由'),
    441: ('特雷维里乌斯的幽灵', '种族', '与 Trevorius 姓名统一'),
    482: ('特鲁索恩旅店', '地名', 'Truthorn 是旅店老板姓氏，非真角'),
    534: ('征服者', '物品', '译名字段去除英文加解释括注，原名保存在 source'),
    539: ('加利博尼姆', '地名', 'source 混入中文注释，改回 Galibornium'),
    541: ('至大之刃', '物品', '译名字段去除英文加解释括注'),
    542: ('黄金圣体光', '物品', '与 golden monstrance 统一'),
    560: ('普特蒙之墓', '地名', 'Pteremon 为人物名，与 Augustin Pteremon 相联，非翼龙'),
    569: ('沃尔夫希尔的首级', '物品', '与 wolf-prince Wulfhyrr 核心译名统一'),
    600: ('邦哈特之锤', '物品', '与 Bonhart de Brague / 完整锤名统一'),
    620: ('神罚灾难', '其他', '此处 Scourge 与灾难语境一致，避免上帝之鞭作为武器理解'),
    628: ('修会项链', '物品', '原文19465明确是兄弟会标志，Order 非秩序'),
    654: ('拉什加尔的首级', '物品', '与 Orc Khan Rashgar 姓名统一'),
    602: ('艾伦尼亚字母表', '其他', '保留 alphabet 字母表语义，统一民族名称'),
    730: ('法力药水', '物品', 'Mana 统一法力'),
    750: ('军械店', '地名', '店铺为地点，不是物品'),
    818: ('异教战争', '事件', '战争为事件而非组织'),
    918: ('善恶值', '其他', '原文23985明确刑讯无辜者会降低数值，不写阵营/善恶值双选'),
    1018: ('裁判庭法官', '身份', 'curial 与教区 diocesan 区分'),
    1042: ('守护者', '物品', '译名字段去除英文加解释括注'),
    1043: ('篡位者', '物品', '译名字段去除英文加解释括注'),
    1066: ('鞭笞者', '组织', '原文 SkillDesc_12 说明为鞭笞派团体，非种族'),
    1085: ('还魂尸', '种族', '与 revenants 统一，不能与所有亡灵混同'),
    1102: ('圣战', '事件', '战争事件而非组织'),
    1131: ('警长', '身份', '与游戏内 Sheriff 具体人名译法一致'),
    1142: ('拉特兰语', '其他', '原文11200等明确外语列表，非地点'),
    1219: ('艾伦尼亚人', '种族', '原文2098明确异教民族，与 Elenians 一致'),
    1225: ('灯神', '种族', '与 genies 一致，避免与精灵混同'),
    1242: ('恐惧', '其他', '状态/概念，不是生物种族'),
    1244: ('埃雷博恩帝国覆灭', '事件', '帝国覆灭是事件，非组织'),
    1247: ('宗教裁判总长科门多尼', None, '补全原文 Commendoni 人名'),
    1248: ('宗教裁判法官瓦拉里安', None, '补全原文 Vallarian 人名'),
    653: ('拉什加尔之拳', '物品', '与 Rashgar 人名统一'),
    510: ('洛奇兰帝国', '地名', '与 Empire of Lochland 同一帝国名称统一'),
    17: ('圣吉里安·洛奇兰修道院', '地名', '与 Saint Jillian 名字统一'),
    871: ('单刃直剑', '物品', '原文22463描述长直剑刃，背剑是对 back 的错误直译'),
    1113: ('细刃匕首', '物品', 'stiletto 为细长刺击匕首，避免细剑匕首混合名称'),
    603: ('皇帝广场', '地名', '固定地名与 Emperor\'s Square 统一'),
    970: ('帝国广场', '地名', 'Empire 与 Emperor 区分，保留原文不同词的含义'),
    727: ('洛奇兰语', '其他', '与 Lochland 地名核心统一'),
}

# Normalize only named components, leaving meaningful surrounding modifiers.
COMPONENTS = [
    (r'布鲁滕莱希|布卢滕赖希|布鲁滕赖希', '布卢滕里希', '统一 Blutenreich 姓氏'),
    (r'圣奥尔塞尼乌斯|圣奥塞纽斯|圣奥特尼乌斯|奥尔塞尼乌斯圣者|奥尔塞尼乌斯|奥塞纽斯', '圣奥塞尼乌斯', '统一 Orthenius 名字'),
    (r'艾雷伯恩|埃里伯恩|埃尔伯恩|埃尔博尼亚|埃雷博尼', '埃雷博恩', '统一 Ereborn/Erebornian 名字核心'),
    (r'艾列尼安|埃莱尼恩|艾伦尼亚|埃伦', '艾伦尼亚', '统一 Elenian/Elene 名字核心'),
    (r'卡尔玛里兰|卡尔玛丽兰|卡尔马利兰', '卡尔马里兰', '统一 Calmariland 名字核心'),
    (r'埃德蒙·达尔维亚(?!斯)', '埃德蒙·达尔维亚斯', '统一 Edmond d\'Arvias 名字'),
    (r'魔力', '法力', '与项目 Mana 术语一致'),
    (r'圣体匣', '圣体光', 'monstrance 祭具术语统一；圣体匣是另一种容器'),
]


def main():
    original = json.loads((ROOT/'glossary_original.json').read_text(encoding='utf-8'))
    source_rows = [r[0] for r in csv.reader((ROOT/'inquisitor_text.csv').open(encoding='utf-8-sig', newline=''))]
    corpus = '\n'.join(source_rows).casefold()
    reviewed = copy.deepcopy(original)
    reviewed.update(characters=[], terms=[], non_translate=copy.deepcopy(original.get('non_translate', [])))
    changes, quarantine = [], []
    def evidence(source):
        pat = re.compile(r'(?<![A-Za-z])'+re.escape(source)+r'(?![A-Za-z])', re.I)
        found = []
        for i,t in enumerate(source_rows,1):
            m=pat.search(t)
            if m:
                found.append(dict(row=i, excerpt=t[max(0,m.start()-100):m.end()+180]))
                if len(found)==2: break
        return found
    for group in ['characters','terms']:
        for index, old in enumerate(original[group]):
            row=copy.deepcopy(old)
            identifier=('C' if group=='characters' else 'T')+str(index)
            fixes=C_FIX if group=='characters' else T_FIX
            reasons=[]
            dest=group
            if index in fixes:
                translation,category,why=fixes[index]
                row['recommended_translation']=translation
                reasons.append(why)
                if category:
                    dest='terms';row.pop('gender',None);row['category_path']=category
                if group=='terms' and index in {419,539}:
                    row['source']={419:'Scourges of God',539:'Galibornium'}[index]
            if group=='terms' and index==200:
                for name in ['orc','orcs','Orcish']:
                    item=copy.deepcopy(row);item['source']=name;item['note']='种族称呼的实际源文变体；拆分合成 source 以确保命中。';reviewed['terms'].append(item)
                changes.append(dict(id=identifier,action='split',before=old,after=['orc','orcs','Orcish'],reasons=['原来的斜杠列表不会按字面匹配实际文本']))
                continue
            for pattern,replacement,why in COMPONENTS:
                # Relevant source guard prevents accidental changes to unrelated names.
                relevant = ('Blutenreich' in row['source'] if 'Blutenreich' in why else
                            'Orthenius' in row['source'] if 'Orthenius' in why else
                            bool(re.search(r'Erebor|Ereborn',row['source'],re.I)) if 'Ereborn' in why else
                            bool(re.search(r'Elen',row['source'],re.I)) if 'Elenian' in why else
                            bool(re.search(r'Calmariland|Kalmariland',row['source'],re.I)) if 'Calmariland' in why else
                            "d'Arvias" in row['source'] if "d'Arvias" in why else
                            'monstrance' in row['source'].lower() if 'monstrance' in why else 'Mana' in row['source'])
                if relevant:
                    new=re.sub(pattern,replacement,row['recommended_translation'])
                    if new!=row['recommended_translation']:
                        row['recommended_translation']=new;reasons.append(why)
            # A name beginning with a title must retain that title in a full-name term.
            title_patterns=[(r'^Grand Master\b|^Grandmaster\b','大团长'),(r'^Pope\b','教皇'),(r'^King\b','国王'),
                            (r'^Brother\b','修士'),(r'^Priest\b|^Father\b','神父'),(r'^Succubus\b','魅魔')]
            if dest=='characters':
                for pattern,title in title_patterns:
                    if re.search(pattern,row['source'],re.I) and not any(w in row['recommended_translation'] for w in [title,'王','教宗','兄弟','祭司'] if w):
                        row['recommended_translation']+=title;reasons.append('补全原文人物称谓 '+title)
                        break
            if dest=='terms' and row.get('category_path') not in {'身份','物品','组织','地名','技能','种族','其他'}:
                old_category=row.get('category_path','')
                row['category_path']='物品' if old_category=='文献' else '其他'
                reasons.append('AINiee 不支持分类 '+old_category+'；规范为 '+row['category_path'])
            if row['source'].casefold() not in corpus or not row['recommended_translation'].strip() or row['recommended_translation']=='——':
                quarantine.append(dict(id=identifier,original=old,proposed=row,reason='当前源文未命中或没有可用译名；不作为启用术语',evidence=evidence(row['source'])))
                continue
            if group=='terms' and index==1266:
                quarantine.append(dict(id=identifier,original=old,reason='heck 是普通感叹词，没有固定专名语义；原表译名为空'))
                continue
            if group=='terms' and index in {904,1065}:
                quarantine.append(dict(id=identifier,original=old,reason={
                    904:'Raptorman 是资源 raptor_man01 等的生物显示名；窃贼缺少支持，需结合生物外观确认译名',
                    1065:'Sildenafilum 是游戏药剂成分的拉丁式名称；西地那芬译法未核实，暂不强制绑定药品名',
                }[index],evidence=evidence(row['source'])))
                continue
            if reasons:
                row['note']='[审校] '+'；'.join(reasons)+('。原备注：'+row.get('note','') if row.get('note') and dest==group else '')
            reviewed[dest].append(row)
            if reasons or dest!=group:
                changes.append(dict(id=identifier,action='move' if dest!=group else 'edit',before=old,after=row,reasons=reasons,evidence=evidence(row['source'])))
    # Add core names lost by substring-based extraction merges. Only actual source
    # occurrences are activated, and complete compound names remain separate.
    aliases={
        'characters':{
            'Tom':'汤姆','Satan':'撒旦','Archangel Gabriel':'大天使加百列','Gabriel':'加百列','Arthamon':'阿尔萨蒙',
            'Father Frederick':'弗雷德里克神父','Saint Nusmiel':'圣努斯米尔','Saint Berthold':'圣伯特霍尔德',
            'Braham':'布拉汉',"En'Lenius":'恩·莱尼乌斯','Gubring':'古布林','Saint Orthenius':'圣奥塞尼乌斯',
            'Pteremon':'普特蒙','Christoffer de Malamert':'克里斯托弗·德·马拉梅特','Jean de Guise':'让·德·吉斯',
            'Enrie Jungwirdt':'恩丽·容维特','Ellisia Würtenrodt':'艾莉西亚·维尔滕罗特',
            'Kenthwaar':'肯斯瓦尔','Zan Drem':'赞·德雷姆','Juhasz Gotherr':'尤哈什·戈特尔',
            'Downay':'道奈','Nicolas':'尼古拉斯','Quentinus':'昆提努斯',
            'Vallarian':'瓦拉里安','Goffred':'戈弗雷德','Commendoni':'科门多尼',
        },
        'terms':{
            'Ereborn':'埃雷博恩','Erebornian':'埃雷博恩','Elenian':'艾伦尼亚','Lochland':'洛奇兰',
            'Calmariland':'卡尔马里兰','Ultherst':'乌尔瑟斯特','Inquisitor':'审判官','Inquisition':'宗教裁判所',
            'Holy Office':'圣务院','Paladin':'圣骑士','Priest':'牧师','Thief':'盗贼',
            'Mana':'法力','Stamina':'耐力','Strength':'力量','Dexterity':'敏捷','Constitution':'体质','Intelligence':'智力','Speed':'速度',
            'Blutenreich':'布卢滕里希','Brotherhood of the Righteous':'正义兄弟会',
        },
    }
    known={r['source'].casefold() for g in ['characters','terms'] for r in reviewed[g]}
    for group,items in aliases.items():
        for source,translation in items.items():
            ev=evidence(source)
            if source.casefold() in known or not ev:continue
            row=dict(source=source,recommended_translation=translation,note='[审校补充] 与已核对的复合词/人物核心译名统一，保留实际原文匹配。')
            row['gender' if group=='characters' else 'category_path']='其他'
            row['occurrence_count']=sum(bool(re.search(r'(?<![A-Za-z])'+re.escape(source)+r'(?![A-Za-z])',t,re.I)) for t in source_rows)
            reviewed[group].append(row);known.add(source.casefold())
            changes.append(dict(id='ADD:'+source,action='add',after=row,reasons=['补充实际命中的核心称谓/别名'],evidence=ev))
    # Exact source conflicts across tables are never silently overwritten.
    conflict_map={}
    for group in ['characters','terms']:
        for row in reviewed[group]:conflict_map.setdefault(row['source'].casefold(),[]).append((group,row))
    conflicts=[v for v in conflict_map.values() if len(v)>1]
    reviewed['stats']=dict(character_count=len(reviewed['characters']),term_count=len(reviewed['terms']),non_translate_count=len(reviewed['non_translate']))
    reviewed['stats']['total_hits']=sum(reviewed['stats'].values())
    reviewed['review_metadata']=dict(date='2026-10-12',original_sha256=hashlib.sha256((ROOT/'glossary_original.json').read_bytes()).hexdigest())
    report=dict(original_counts={k:len(original[k]) for k in ['characters','terms']},reviewed_counts=reviewed['stats'],
                changes=changes,quarantine=quarantine,exact_source_conflicts=conflicts)
    (ROOT/'glossary_reviewed.json').write_text(json.dumps(reviewed,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'glossary_review_changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Counts:',report['reviewed_counts'],'changes',len(changes),'quarantine',len(quarantine),'source conflicts',len(conflicts))


if __name__=='__main__':main()
