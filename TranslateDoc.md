# Inquisitor AINiee 翻译操作指南

准备已完成。共 **24,074 条**去重英语原文、4,474,170 个字符，对应 **61,204 处**资源位置。界面、任务日志、人物/物品名称与说明、三职业对话已合并；相同原文只译一次，通过 `text_locations.jsonl` 回填所有位置。去重合并的短句仍需结合语境审校。

## 文件与顺序

- `inquisitor_text.csv`：正式原文，无表头，单列 UTF-8 BOM。不要修改顺序。
- **`inquisitor_ainiee_input.csv`：拖入 AINiee 的文件**，仅比正式原文多一行 `source` 表头。本地 CsvReader 会把首行当表头；直接导入正式原文会漏译第一条。
- `ainiee_exclusion_list.json`：已人工复核的 5 条禁翻规则。
- `placeholder_report.md`：标记统计与误判修正说明。
- `translation_prompt.txt`：可追加到 AINiee 提示词中的完整项目指令。
- `import_translation.py`：去除 AINiee 表头，严格校验并导入正式译文。

## 启动与配置

```powershell
Set-Location D:\StaticHanHua\Tools\AINiee
.\venv\Scripts\python.exe AiNiee.py
```

1. 在「接口管理」选择你已配置的接口与模型；可使用 DeepSeek。未读取或更改 API 密钥，需在界面确认可用接口。
2. 设置源语言英语、目标语言简体中文。
3. 打开「禁翻表」，导入本项目 `ainiee_exclusion_list.json`，打开顶部开关，点击保存。换项目时注意切换规则。
4. 打开「翻译设置」的「自动处理文本代码段」，让匹配标记在译前占位、译后还原。
5. 按提示词页面的操作方式追加 `translation_prompt.txt`；确认其中 textarea 输出块保留。不要把 `{target_language}` 当游戏变量禁翻。
6. 在术语表统一下列建议译名，之后可以按游戏语境调整。

| 英文 | 建议译名 |
|------|------|
| Paladin / Priest / Thief | 圣骑士 / 牧师 / 盗贼 |
| Inquisitor / Inquisition | 审判官 / 宗教裁判所 |
| Holy Office | 圣务院 |
| Brotherhood of the Righteous | 正义兄弟会 |
| Hit Points / Mana / Stamina | 生命值 / 法力 / 耐力 |
| Strength / Dexterity / Constitution | 力量 / 敏捷 / 体质 |
| Intelligence / Speed | 智力 / 速度 |

7. 将 **inquisitor_ainiee_input.csv** 拖入输入框，输出目录建议设为本项目 `ainiee_output`。
8. 开始翻译。文本量较大，建议使用 AINiee 的缓存与续译，先检查一批结果再继续。不要手工拆分或重排正式 CSV。

## 保护规则

| 类型 | 次数 | 示例 / 要求 |
|------|------|------|
| 完整双美元变量 | 119 | `$$X$$`、`$$var:HracHodil$$`，包含边界与参数 |
| printf 和百分号 | 196 | `%+d`、`%s`、`%%`；参数保持顺序 |
| 字面换行转义 | 1,125 | 1,124 个含双反斜杠，1 个含单反斜杠，按原文保留 |
| 转义尖括号边界 | 2 | `\<`、`\>`；内部 New Save 译为新建存档 |
| 真实 CRLF | 1 | 原文第 17,943 条；是合法字段内换行，不能盲目修复 |

单条最多 25 处保护匹配，低于本地 AINiee 的 50 匹配上限。不要导入通用尖括号规则，否则 New Save 会被跳过；不要使用仅匹配 `$word` 的规则，否则会破坏双美元表达式。

## 导入译文与校验

AINiee 输出仍含 `source` 表头。完成后，将下面的路径换成实际输出 CSV；脚本只在结构与标记校验通过后写出 `inquisitor_text_translated.csv`，不会翻译或覆盖已有正式译文。

```powershell
Set-Location D:\StaticHanHua\Projects\inquisitor
python .\import_translation.py ".\ainiee_output\实际输出文件.csv"
```

如果译文已经无表头：

```powershell
python .\import_translation.py .\inquisitor_text_translated.csv --check
```

检查逻辑记录数、单列结构、空译文、完整变量及冒号参数、printf 顺序、反斜杠数量、转义尖括号和真实换行。失败生成 `need_retranslate.csv` 与 `translation_validation.json`。校验通过仍需检查未翻译条目和语义质量；人名等可能与英语原文相同，不能仅凭原文相同就判定漏译。

通用技能校验命令可作额外参考，但会把可见 New Save 误当 XML，且默认换行修复会改动本项目唯一的合法 CRLF；**本项目以专用严格校验为准，不盲目使用 `--fix-newlines`**。

## 当前边界

资源提取与翻译准备完成，尚未执行实际翻译。默认由你在 AINiee 界面启动任务。本阶段未修改游戏文件，也未进行中文字体或游戏内显示验证。地图二进制、图片内文字及 EXE 硬编码文字尚未确认完整覆盖；正式回填前还需检查运行时补丁优先级、中文字体及 CharConvert 字符转换表。
