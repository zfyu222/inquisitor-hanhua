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
- 当前阶段：初始化完成，尚未提取、翻译或回填。

## 技术栈
| 环节 | 工具 | 版本 / 状态 |
|------|------|------|
| 初始化 | start-translate / init_game_project.py、Git、Windows junction | 工作区当前脚本；独立 main 分支仓库 |
| 资源探测 | Python struct / 文件头只读检查 | 已确认 x86 PE、无 CLR、DAT 文件头 DRPK |
| 提取 | 待选择 DAT 解包工具；必要时 IDA Pro + IDA MCP | 未执行 |
| 翻译 | 计划使用 AINiee，接口与模型待确定 | 未执行 |
| 回填 | 待确认 DAT 重建与字体方案 | 未执行 |
| 发布 | game-release-patch | 未执行 |

## 文本提取
- 游戏入口：`Game/Game/Inquisitor.exe`。外层 Game 是安装根目录链接，内层 Game 是游戏自带子目录。
- 资源线索：`Game/Game/01_local.dat`（12,459,909 字节）、`01_data.dat`（1,021,739 字节）、`02_patch.dat`（20,427,520 字节），三个文件前四字节均为 ASCII DRPK。
- 01_local.dat 是按名称判断的本地化候选包，内部内容尚未确认；补丁覆盖顺序待确认。
- 下一步：使用 game-unpack 分析 DRPK 目录、压缩/编码和补丁覆盖关系，定位文本与字体；必要时分析 EXE 资源读取逻辑。
- 输出：项目根目录 `inquisitor_text.csv`，单列，每条文本一个 CSV 记录；另保留定位映射供回填。
- 初始化仅做只读探测，未修改游戏文件。

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
- DRPK 格式、文本编码和资源优先级尚未解析。
- 中文字形、字库容量、换行与界面长度限制尚未验证。
- 尚无可运行汉化产物或对外补丁。

## 对外发布
- 补丁文件：未生成。
- 支持版本/平台：拟针对当前 Steam Windows 英语版 Build 6307888，兼容性待验证。
- 载荷、验证结果与发布已知问题：待回填完成后记录。

## 版本记录
- 2026-10-11 - 初始化 Projects/inquisitor，建立安装根目录 junction、独立 Git 仓库与档案。
- 2026-10-11 - 补充 Steam 官方资料、本地构建信息、原生 PE 与 DRPK 资源线索。
