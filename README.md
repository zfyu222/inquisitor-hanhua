# Inquisitor 汉化项目

## 游戏信息
- 原名：Inquisitor（Steam App ID：241620）。
- 中文名：暂译《审判官》，非官方译名。
- 开发商 / 发行商：CINEMAX GAMES。
- 平台：本项目针对 Steam Windows 版。
- 发售日期：Steam 商店标示 2012-09-05。
- 支持语言：商店列出英语、捷克语、西班牙语（西班牙）、法语、意大利语界面与字幕，未列出中文。
- 本次源语言：英语，本地 Steam 清单的 UserConfig 和 MountedConfig 均为 english；最初创作语言待确认。
- 引擎及版本：待确认。本地为 x86 32 位原生 PE，CLR 数据目录为零，未发现 Unity / Mono / RPG Maker 典型目录结构。
- 安装目录：`D:\Program Files (x86)\Steam\steamapps\common\Inquisitor`。
- 本地版本：Steam Build ID `6307888`；Changelog.txt 首条为 v1.10.18，日志不作为当前 EXE 版本的最终证明。
- 依据：[Steam 官方商店](https://store.steampowered.com/app/241620/Inquisitor/?l=english)，本地 appmanifest_241620.acf、安装目录及文件头检查（2026-10-11）。

## 游戏简介
本作是一款黑暗奇幻题材的等距视角角色扮演游戏，结合战斗、探索与宗教案件调查。玩家可选择圣骑士、牧师或盗贼，在遭受灾难的 Ultherst 收集证据、调查异端，并承担审判选择的后果。大量剧情与对话需要统一人名、地名和宗教术语。[来源：Steam 官方商店](https://store.steampowered.com/app/241620/Inquisitor/?l=english)

开发者在商店提示频繁暴力或血腥、一般成人内容；剧情涉及刑讯与宗教迫害。[来源：Steam 官方商店](https://store.steampowered.com/app/241620/Inquisitor/?l=english)

## 汉化目标
- 范围：计划覆盖游戏内界面、对话、任务、物品与技能说明，实际覆盖范围在提取后确认。
- 目标语言：简体中文。
- 随附 PDF、小说、原声及额外内容暂不纳入游戏内文本范围。
- 当前阶段：AINiee 译文修复与结构校验完成，已生成正式译文；待回填与中文字体/游戏内验证。

## 技术栈
| 环节 | 工具 | 版本 / 状态 |
|------|------|------|
| 初始化 | start-translate / init_game_project.py、Git、Windows junction | 工作区当前脚本；独立 main 分支仓库 |
| 资源探测 | Python struct / 文件头只读检查 | 已确认 x86 PE、无 CLR、DAT 文件头 DRPK |
| 提取 | DRPK / SFL Python 解包、标签提取与去重映射 | Python 3.12.10；项目 drpk_extract.py / extract_text.py |
| 翻译 | AINiee + 项目专用标记分析与严格校验 | 缓存模型 mimo-v2.6-flash；5 组严格规则及通用精确例外校验通过 |
| 回填 | 待确认 DAT 重建与字体方案 | 未执行 |
| 发布 | game-release-patch | 未执行 |

## 文本提取
- 工具：Python 3.12.10，`drpk_extract.py` 与 `extract_text.py`；QuickBMS 0.12.0 交叉校验；Git 2.53.0.windows.1。
- 依据：[Luigi Auriemma Inquisitor BMS 脚本](https://aluigi.altervista.org/bms/inquisitor.bms)、[QuickBMS SFL 分块定义](https://github.com/LittleBigBug/QuickBMS/blob/master/src/unz.c)、[iMatix SFL 文档](https://imatix-legacy.github.io/sfl/sfldoc.htm)。格式为 DRPK、XOR 0x4A、SFL 分块；Python 实现已验证全部提取条目的解压长度。
- 原始包：`Game/Game/01_local.dat`、`01_data.dat`、`02_patch.dat`，只读操作。解压资源在 `extracted/`，不入库。
- 命令（在项目目录）：`python drpk_extract.py Game/Game/01_local.dat extracted/01_local`；对 01_data、02_patch 同样运行，再执行 `python extract_text.py`。
- 按相同资源路径使用 02_patch 覆盖基础包；共覆盖 359 份提取资源。该顺序基于补丁结构推定，回填时还需运行时确认。
- 文本为 UTF-16 LE BOM 的类 XML 文件；提取 1,433 份本地化资源内 61,204 处显示文本，按精确字符串去重为 **24,074 条**，总字符数 4,474,170。
- 字段：string 59,377 处、visname 859 处、desc 469 处、text 344 处、title 114 处、NPCName 41 处。不翻译 name/id/action/cond 等逻辑字段与 CharConvert 字符表。
- `inquisitor_text.csv`：无表头，单列 UTF-8 BOM；`text_locations.jsonl`：记录 CSV 行号、来源包、文件、标签、ID、字符区间；`extraction_report.json`：源文件 SHA-256 与统计。
- 校验：全部输出记录通过单列读取与源资源逐位置反向核对；QuickBMS 0.12.0 对照 1,800 份解压文件，全部逐字节一致（extraction_crosscheck.json）。DLT 字符串标签完整配对检查通过。对话引用检查详见 dialogue_audit.json；Nicolas 三职业存在 86 与 086 的原始写法差异，数值 ID 对应同一条，实际引擎解析方式待回填核实。
- 未宣称全文覆盖：地图二进制/图片文字/EXE 硬编码显示文本尚未完成核实。抽查 01_levels.dat 为 MAP/MPSC/LGFX 二进制资源。

## 翻译
- 2026-10-13 修复验收：已生成根目录 `inquisitor_text_translated.csv`，24,074 条无表头单列译文。修复 23 条转义异常、新建存档漏译及“敲诈”错字，并统一经核对的专名/称谓，共改变 312 条。原导出、AINiee 缓存及游戏文件未修改。详细逐条依据、验收哈希及报告在 `TranslateFiles/repair_20261013_v2/`。
- 全部 265 次术语候选已记录结论：118 次修复后匹配、56 次自然表达保留、91 次普通词/语境误报保留。复核包括此前53条抽样、术语候选及姓名统一项，不宣称全文逐句语义精校。冻结术语表未改动。
- 验证命令：`python TranslateFiles/validate_inquisitor.py inquisitor_text_translated.csv`，项目严格规则0错误，通用检查退出码0。仅将确认属于可见菜单文字的 `<New Save \>` 排除出通用机器标签族；严格规则仍保护两端转义，损坏边界的回归样例已拒绝。第17943条合法CRLF和源文本身的转义异常原样保留。先前未通过报告以下作为历史记录保留。
- 2026-10-13 译后检查：用户提供 `inquisitor_ainiee_input_translated.csv`；24,074 条单列译文、无空译文，对照缓存确认全部原文顺序一致。缓存 23,065 条已翻译、1,003 条已润色、6 条已排除；排除项导出回退为原文。只在 `TranslateFiles/validation_20261013/` 生成去表头检查副本和报告，原导出/缓存/游戏均未修改。
- 当前未通过：23 条转义异常（20 条反斜杠序列/数量差异，3 条新增真实 LF），第 23569 条 New Save 漏译，第 10607 条“敲扎”错字。53 条固定抽样及重点记录语义核对；全表术语扫描有 265 次候选、涉及 243 行，含可接受表达和语境误报，不等于确定错译。详见 `TranslateFiles/validation_20261013/review.md`；未生成正式 `inquisitor_text_translated.csv`。本次检查无需重新选择工作流，沿用 AINiee。
- 新的检查指南在 `TranslateFiles/TranslateDoc.md`。下列准备/术语记录为历史阶段信息，旧中间文件和缓存本次未自动迁移。
- 当前完成的是翻译准备：`TranslateDoc.md`、`placeholder_report.md`、`ainiee_exclusion_list.json`、`translation_prompt.txt` 已生成。实际翻译由用户在 AINiee 执行，接口与模型待选。
- AINiee 导入文件：`inquisitor_ainiee_input.csv`（增加 source 表头，避免本地 CsvReader 漏掉第一条）；正式原文 `inquisitor_text.csv` 保持无表头。
- 5 条人工复核保护规则：完整双美元变量、printf/百分号、保留所有反斜杠的字面转义、转义尖括号、真实 CRLF。单条最多 25 次匹配。
- 通用分析器会误保护 New Save 并漏掉双美元变量冒号参数，已针对本项目修正；唯一真实换行在第 17,943 条，不盲目执行通用 --fix-newlines。
- 必须开启禁翻表与自动处理文本代码段。术语建议和提示词见 TranslateDoc.md / translation_prompt.txt。
- 译后运行 `python import_translation.py <AINiee输出CSV>`，去表头并验证数量、单列、空译文、标记及顺序、完整转义后写出 `inquisitor_text_translated.csv`；已有正式译文用 --check。
- 校验结果：原文单列/资源映射及 AINiee 首行对齐已通过；专用校验工具通过真实 CRLF/标记保留检查，并成功检出变量及反斜杠损坏样例；目前未生成正式译文，译文质量与完整性尚未验证。
- 2026-10-12 术语审校：从项目缓存 `extra.analysis_v1` 冻结 569 条人物、1,267 条术语（共 1,836 条），检查全表来源、译名与分类，并对重点问题查阅原文语境；审校版为 564 条人物、1,275 条术语（共 1,839 条）。44 条隔离待核对，新增 45 条实际命中的核心名称，拆分一条斜杠合成 source，规范不支持的分类。详见 `glossary_review.md` 和 `glossary_review_changes.json`。
- `glossary_original.json` 保留原分析表；`glossary_reviewed.json` 为项目分析表格式，不能当全局词典导入。审校未修改活动缓存；关闭 AINiee 后，可按 TranslateDoc.md 使用 `apply_reviewed_glossary.py --apply` 安装。脚本先检查原表是否变化并备份完整缓存，仅替换分析表，保留翻译进度；默认运行只检查。
- 应用状态（2026-10-12）：已按用户要求安装审校版，共 1,839 条。应用前 AINiee 未运行；完整原缓存备份为 `AiNieeCache/glossary_review_backups/AinieeCacheData_20261012_011454_858451.json`。校验确认仅 `extra.analysis_v1` 改变，缓存中的其他字段、翻译结果与进度均保持一致。
- 通用功能沉淀（2026-10-12）：共享检查/构建/安全应用程序位于工作区 `Tools/localization/glossary_tool.py`，后续各游戏按固定术语审校流程使用。项目 `apply_reviewed_glossary.py` 已改为调用共享安全应用逻辑，原有操作命令保持可用；具体译名修正保留在本项目，不带入其他游戏。

## 回填
- 工具/命令：待确定。
- 步骤：先确认格式、编码、中文字体与补丁加载机制，再确定可逆回填方案。
- 验证方法：后续检查启动、主菜单、对话、任务日志、物品/技能提示、存读档与中文显示。

## 已知问题
- DRPK 索引、XOR 与 SFL 解压已解析，尚未验证重建与游戏加载。
- 中文字形、字库容量、CharConvert 转换表、换行及界面长度限制尚未验证。
- NPCName 显示字段另标为 display_name_review_lookup，回填前须排查是否兼作内部查找值。
- 全文去重可能合并不同语境的短句，需翻译审校；保留所有资源位置供后续按语境拆分。
- 正式译文已通过结构和占位符校验；未进行全文逐句语义精校，尚无可运行汉化产物或对外补丁。

## 对外发布
- 补丁文件：未生成。
- 支持版本/平台：拟针对当前 Steam Windows 英语版 Build 6307888，兼容性待验证。
- 载荷、验证结果与发布已知问题：待回填完成后记录。

## 版本记录
- 2026-10-11 - 初始化 Projects/inquisitor，建立安装根目录 junction、独立 Git 仓库与档案。
- 2026-10-11 - 补充 Steam 官方资料、本地构建信息、原生 PE 与 DRPK 资源线索。

- 2026-10-11 - 提取 24,074 条去重原文，保留 61,204 处映射并校验源文本；游戏资源未修改。
- 2026-10-11 - 完成 AINiee 专用导入文件、占位符保护、翻译提示词及严格译后导入工具，进入翻译阶段。
- 2026-10-11 - QuickBMS 对照 1,800 份资源逐字节一致；验证 AINiee 全量导入对齐及严格校验工具，CSV 禁用 Git 换行转换。
- 2026-10-12 - 审查 AINiee 已提取术语表，生成审校版、逐项修改与隔离清单及带备份的应用脚本；未改动活动缓存或游戏文件。
- 2026-10-12 - 将审校版应用到 AINiee 项目缓存，备份原缓存并逐字段验证翻译进度等其他数据保持一致。
- 2026-10-12 - 将安全应用功能切换为共享工具调用，验证当前术语仍完整安装；工作区建立固定审校流程与共享自动检查/构建/应用工具。
- 2026-10-13 - 检查用户提供的 24,074 条 AINiee 译文，验证缓存对应并记录 23 条转义异常、漏译/错字及术语候选；报告放 TranslateFiles，未修改用户译文或生成已验收正式译文。
- 2026-10-13 - 完成转义、漏译、错字及名称一致性修复，共312条；复核全部265次术语候选，严格与通用精确例外检查通过，生成正式译文，游戏内回填仍待验证。
