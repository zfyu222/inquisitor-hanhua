# Inquisitor 术语表审校报告

审校日期：2026-10-12。输入为 AINiee 项目缓存的 `extra.analysis_v1`，已冻结到 `glossary_original.json`。原表为 **569 条人物 + 1,267 条术语 = 1,836 条**。

已逐条检查 source、建议译名和分类，并对关键错译、复合名称、名称合并和可疑生物名查阅提取原文。备注仅针对发现的重点问题修正，不代表所有背景描述均经核实，也不代表正文翻译已经完成。

## 结果

- 审校版：**564 条人物 + 1,275 条术语 = 1,839 条**。
- 修改记录 202 项：编辑 135 项、移类 21 项、拆分 1 项、补充 45 项。
- 隔离 **44 条**，保留原条目和理由，没有删除原始快照。隔离项不参与固定术语绑定，也不是禁翻项。
- 结构检查通过：全部启用 source 在源文本中有匹配，无空译名、无不区分大小写的同源重复；分类符合本地 AINiee 支持值，原分析版本/状态/时间与禁翻表保留。完整原条目数量可按移类、拆分、隔离和新增核算。
- 当前活动缓存和游戏文件均未修改。应用脚本的默认检查已运行，前后缓存 SHA-256 一致。

## 主要问题

| 原文 | 原表问题 | 审校结果 / 依据 |
|---|---|---|
| Golden Tome of the Defender of the Faith | 译成「汤姆」，误当人物 | 信仰捍卫者金典；第 22198 条明确是书籍别称，移至物品 |
| Mansion of Baron Dawn von Blutenreich | 省掉庄园，误当男爵 | 道恩·冯·布卢滕里希男爵庄园；移至地名 |
| On the Invocation of Satan and Other Infernal Minions | 只译「撒旦」 | 论撒旦及其他地狱仆从的召唤；保留完整书名 |
| signet ring of the Knights of Archangel Gabriel | 只译天使名 | 大天使加百列骑士团印戒；完整物品名 |
| Chapter of the Brotherhood of the Righteous | 译成「教区」 | 正义兄弟会分会；区分组织分会与 diocese |
| Scourges of God中怪物 | source 混入中文说明；归类怪物 | source 改为 Scourges of God，译为神罚灾难；原文描述饥荒、瘟疫、火雨 |
| Galibornium异教城市 | source 混入中文说明 | source 恢复 Galibornium |
| orc / orcs / Orcish | 合成 source 无法按字面命中 | 拆为三条，保留各自词形 |
| Pteremon's Tomb | 将名称译成「翼龙」 | 普特蒙之墓，保留专名 |
| Backsword | 背剑 | 单刃直剑；第 22463 条为直刃武器描述 |
| Genie / genies | 精灵 | 灯神；与 elf 对应的精灵区分 |
| Kind Edward | 把错拼 Kind 当人名 | 爱德华国王；第 18151 条描述国王颁布禁赌法令 |
| 月光斩 / 精灵族 | 原文无匹配 | 隔离；与本地分析提示词示例一致，不能加入本游戏固定术语 |

复合词统一了 Blutenreich（布卢滕里希）、Orthenius（圣奥塞尼乌斯）、Ereborn（埃雷博恩）、Elenian（艾伦尼亚）、Calmariland（卡尔马里兰）、d'Arvias（达尔维亚斯）及 Mana（法力）等写法。补充实际源文出现的核心人名，避免原来的长物品名合并吞掉人物条目。完整人物名称补回遗漏的国王、教皇、大团长、神父等称谓。

`monstrance` 保留并统一为「圣体光」，没有把原表中正确的「圣体光」改成圣体匣。[Getty AAT](https://www.getty.edu/vow/AATFullDisplay?find=jug&logic=AND&note=&page=1&subjectid=300083005) 收录该中文称呼；[中国天主教礼仪说明](https://www.chinacatholic.cn/ccic/report/2605/0071-1.htm) 区分圣体盒、圣体匣与显供圣体光座。

## 待确认与审校边界

- Raptorman：原表「窃贼」没有支持；原始资源是 `raptor_man01` 等生物显示名。需要生物外观或更完整设定，暂不指定「迅猛龙人」等未经验证的译名。
- Sildenafilum：属于游戏药剂成分的拉丁式名称，「西地那芬」译法未核实；不强制套用真实药品名称。
- Saint Jilliam / Saint Jillian、Heidrick / Heindrick 等不同拼写：保留源文差异，不能仅凭相似拼写认定同一人物。
- Transubstantiation：游戏语境涉及将活物化石，不直接套用宗教圣体教义译名。
- Victor's Pride：原文并不能证明 Victor 是 Victor Hammerhand，未强制绑定为该人物。
- 未命中 source 可能是拼写变体、模型概括或错误提取；除明确的提示词示例外，没有把所有未命中条目一律判为虚构。
- 核对的是术语质量与项目格式，尚未进行游戏内显示验证。已生成正文不会自动按新术语回改。

## 使用文件

- `glossary_original.json`：原分析表快照。
- `glossary_reviewed.json`：可应用的项目分析表，不是全局词典格式。
- `glossary_review_changes.json`：逐项 before/after、理由、原文记录号和摘录，以及完整隔离条目。
- `review_glossary.py`：从快照生成审校版，不读取或写入活动缓存。
- `apply_reviewed_glossary.py`：默认只检查。正常退出 AINiee 后用 `--apply` 应用，拒绝原表已变化的情况，备份完整缓存，仅替换 `extra.analysis_v1`。步骤见 TranslateDoc.md。

## 隔离清单

| 编号 | source | 原译名 | 理由 |
|---|---|---|---|
| C72 | Archbishop Clement III | 大主教克莱门特三世 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C158 | Princess Theresie | 特蕾西公主 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C184 | King Joachim XII | 约阿希姆十二世国王 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C472 | Astaroth | 阿斯塔罗特 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C490 | Vernicus | 维雷尼库斯 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C500 | Halvard | 哈尔瓦德 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C566 | Adrian Luther | 阿德里安·路德 | 当前源文未命中或没有可用译名；不作为启用术语 |
| C567 | broadcaster |  | 当前源文未命中或没有可用译名；不作为启用术语 |
| C568 | Bentlach | 本特拉赫 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T91 | Battle of Erstwick Crusades | 厄斯特威克十字军战役 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T93 | Wolf-Prince's bestial spawn | 狼王子的兽类后代 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T101 | Key to Hillbrandt's Tower | 希尔布兰特高塔之钥 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T213 | High Priest of Fire | 火焰至高祭司 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T270 | Death of the Dead | 亡者之舞 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T342 | Neckace of Death | 死亡之链 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T346 | Paladins of Hell | 地狱圣骑士 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T474 | grand alchemist | 大炼金术师 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T499 | 月光斩 | 月光斩 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T500 | 精灵族 | 精灵族 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T513 | seal-like relic | 戒指状圣遗物 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T535 | Endarian's Bane | 恩达里安之祸 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T545 | Imperial family | 皇室家族 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T657 | Royal Assembly | 王国议会 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T771 | landskecht | 雇佣兵 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T794 | Blumenheim | 布卢门海姆 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T817 | Orc's Bane | 兽人克星 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T904 | Raptorman | 窃贼 | Raptorman 是资源 raptor_man01 等的生物显示名；窃贼缺少支持，需结合生物外观确认译名 |
| T909 | Star Gate | 星门 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T922 | gardeners | 园丁 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T936 | strx | 女妖 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T975 | Healer potion | 治疗药水 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T987 | Power of keys | 钥匙之秘 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1034 | Daemon's Maw | 恶魔之口 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1041 | Earthen Rite | 大地仪式 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1055 | Lord's Hound | 主之猎犬 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1065 | Sildenafilum | 西地那芬 | Sildenafilum 是游戏药剂成分的拉丁式名称；西地那芬译法未核实，暂不强制绑定药品名 |
| T1073 | darkest cult | 暗黑教团 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1169 | apricot | 阿普里恩 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1237 | strix | 斯特里克斯 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1251 | Ordinary Calmariland language | 卡尔马利兰语 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1259 | Tower of the Truth | 真相之塔 | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1260 | Kali's Blessing |  | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1261 | Hellbringer | —— | 当前源文未命中或没有可用译名；不作为启用术语 |
| T1266 | Heck |  | 当前源文未命中或没有可用译名；不作为启用术语 |
