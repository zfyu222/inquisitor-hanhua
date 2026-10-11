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
- 当前阶段：文本提取与 AINiee 翻译准备完成，待用户执行实际翻译。

## 技术栈
| 环节 | 工具 | 版本 / 状态 |
|------|------|------|
| 初始化 | start-translate / init_game_project.py、Git、Windows junction | 工作区当前脚本；独立 main 分支仓库 |
| 资源探测 | Python struct / 文件头只读检查 | 已确认 x86 PE、无 CLR、DAT 文件头 DRPK |
| 提取 | DRPK / SFL Python 解包、标签提取与去重映射 | Python 3.12.10；项目 drpk_extract.py / extract_text.py |
| 翻译 | AINiee + 项目专用标记分析与严格校验 | 5 条保护规则，待用户选择接口与模型 |
| 回填 | 待确认 DAT 重建与字体方案 | 未执行 |
| 发布 | game-release-patch | 未执行 |

## 文本提取
- 工具：Python 3.12.10，`drpk_extract.py` 与 `extract_text.py`；Git 2.53.0.windows.1。
- 依据：[Luigi Auriemma Inquisitor BMS 脚本](https://aluigi.altervista.org/bms/inquisitor.bms)、[QuickBMS SFL 分块定义](https://github.com/LittleBigBug/QuickBMS/blob/master/src/unz.c)、[iMatix SFL 文档](https://imatix-legacy.github.io/sfl/sfldoc.htm)。格式为 DRPK、XOR 0x4A、SFL 分块；Python 实现已验证全部提取条目的解压长度。
- 原始包：`Game/Game/01_local.dat`、`01_data.dat`、`02_patch.dat`，只读操作。解压资源在 `extracted/`，不入库。
- 命令（在项目目录）：`python drpk_extract.py Game/Game/01_local.dat extracted/01_local`；对 01_data、02_patch 同样运行，再执行 `python extract_text.py`。
- 按相同资源路径使用 02_patch 覆盖基础包；共覆盖 359 份提取资源。该顺序基于补丁结构推定，回填时还需运行时确认。
- 文本为 UTF-16 LE BOM 的类 XML 文件；提取 1,433 份本地化资源内 61,204 处显示文本，按精确字符串去重为 **24,074 条**，总字符数 4,474,170。
- 字段：string 59,377 处、visname 859 处、desc 469 处、text 344 处、title 114 处、NPCName 41 处。不翻译 name/id/action/cond 等逻辑字段与 CharConvert 字符表。
- `inquisitor_text.csv`：无表头，单列 UTF-8 BOM；`text_locations.jsonl`：记录 CSV 行号、来源包、文件、标签、ID、字符区间；`extraction_report.json`：源文件 SHA-256 与统计。
- 校验：全部输出记录通过单列读取与源资源逐位置反向核对。DLT 字符串标签完整配对检查通过。对话引用检查详见 dialogue_audit.json；Nicolas 三职业存在 86 与 086 的原始写法差异，数值 ID 对应同一条，实际引擎解析方式待回填核实。
- 未宣称全文覆盖：地图二进制/图片文字/EXE 硬编码显示文本尚未完成核实。抽查 01_levels.dat 为 MAP/MPSC/LGFX 二进制资源。

## 翻译
- 译文输出：`inquisitor_text_translated.csv`，与原文逐条对应。
- 词典：待建立，优先统一职业、宗教称谓、人名、地名、法术与物品术语。
- 策略：提取后使用 game-translate 分析占位符、生成禁翻表与 TranslateDoc.md；默认由用户在 AINiee 完成实际翻译。
- 校验：尚未执行。

## 回填
- 工具/命令：待确定。
- 步骤：先确认格式、编码、中文字体与补丁加载机制，再确定可逆回填方案。
- 验证方法：后续检查启动、主菜单、对话、任务日志、物品/技能提示、存读档与中文显示。

## 已知问题
- DRPK 索引、XOR 与 SFL 解压已解析，尚未验证重建与游戏加载。
- 中文字形、字库容量、CharConvert 转换表、换行及界面长度限制尚未验证。
- NPCName 显示字段另标为 display_name_review_lookup，回填前须排查是否兼作内部查找值。
- 全文去重可能合并不同语境的短句，需翻译审校；保留所有资源位置供后续按语境拆分。
- 尚无实际译文、可运行汉化产物或对外补丁。

## 对外发布
- 补丁文件：未生成。
- 支持版本/平台：拟针对当前 Steam Windows 英语版 Build 6307888，兼容性待验证。
- 载荷、验证结果与发布已知问题：待回填完成后记录。

## 版本记录
- 2026-10-11 - 初始化 Projects/inquisitor，建立安装根目录 junction、独立 Git 仓库与档案。
- 2026-10-11 - 补充 Steam 官方资料、本地构建信息、原生 PE 与 DRPK 资源线索。

- 2026-10-11 - 提取 24,074 条去重原文，保留 61,204 处映射并校验源文本；游戏资源未修改。
