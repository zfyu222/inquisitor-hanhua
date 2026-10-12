# Inquisitor 原生回填分析（2026-10-13）

目标：Steam Windows Build 6307888，EXE SHA-256
`88854166fe459cb1937b075604d906c88c3e1109d7b87fb17cb494939c7a9276`。
连接 IDA Professional 9.3 的 MCP 后完成以下只读分析；没有修改 EXE。

## 资源包

- `0x4B85C0`：枚举 `*.dat`，按名称插入排序后逐个打开。
- `0x4B7650`：读 DRPK 索引，并合并已加载与新加载资源；同目录、同名时选新加载的条目。
- `0x406F80`：目录/文件名比较采用 `CompareStringA(0x409, 1, ..., -1, ..., -1)`。必须按此排序，普通 ASCII 排序会产生 12 组错误邻接。
- footer 最后一个 DWORD 是最大解压资源字节数：三个源包分别为 561828、3258232、3298658，均与所有条目的最大展开长度相等；`0x4B7BBD` 将该值用于最大缓冲区尺寸。
- entry 最后一个 DWORD 是第一个 SFL 压缩块长度，与条目数据前两字节完全一致；不是校验和。新包采用每块最多 16384 字节的 SFL 原始块 `0x80`。
- 独立补丁命名为 `03_zh.dat`，按上述排序加载在 `02_patch.dat` 后。资源只有本地化文字和字体；原包不覆盖。

## 字体

- `0x411C80`：检查 UTF-16 BOM、读取 BFI 各字段与 Character 行，调用 `0x4130D0` 插入字形。
- `0x4130D0`：以 unsigned 16-bit 字符键比较、插入树节点，没有固定 256 字符数组限制。
- `0x525820` / `0x5258A0`：CharConvert 每两个字符组成大小写配对，不命中时返回原字符。中文不需要添加到该表。
- `Nosferatu`、`NosferatuS`、`NosferatuSBlack` 保留原有字形、特殊图标和混合参数。Black 与 S 使用同一原始位图；按原 UV 缩放后扩展到 2048×2048。
- 使用系统 SimHei 16/12 像素字形，补齐译文中原字库缺少的 3429 个字符。fontTools cmap 覆盖检查无缺字；所有译文字码均小于 65536。
- 已生成位图样张；游戏内字体大小、基线、黑字模式和长句排版仍待目视验收。
- 长词/无空格折行：`0x412950` 逐字符累积宽度，在 `0x412C1F` 检查空格机会；没有空格时，`0x412C7B` 至 `0x412CA8` 绘制溢出字符之前的内容，再从该字符开始下一行。配套测量 `0x412D40` 在 `0x413027` 至 `0x41304D` 同样回退按字符折行。中文不需盲目插入空格或额外断行符；实际排版仍需目视确认。

## NPCName

- `0x4B0D0D`：将 NPCName 复制到对象的 UTF-16 缓冲区 +0x358。
- `0x4B3155`：将该缓冲区复制到可见对话行前缀，并追加分隔符，再追加正文。
- 按该数据流确认其用途为说话人显示文字。回填全部 41 处；其他 name/id/action/cond 等逻辑字段未替换。

## 程序与状态

在项目目录运行：

```powershell
python TranslateFiles/validate_inquisitor.py inquisitor_text_translated.csv
python build_patch.py
python deploy_patch.py status
# 以下操作要求先退出游戏
python deploy_patch.py install
python deploy_patch.py remove
python deploy_patch.py restore-settings
```

`build_patch.py` 校验原始资源哈希、精确 span 和全部输出资源重新解包后的字节；字体源缓存有哈希清单。依赖 Python 3.12、Pillow 12.3.0、fontTools 4.63.0，IDA 查询程序另依赖 pefile。

759 份输出资源已通过项目 SFL 解码及 QuickBMS 0.12.0 的独立逐字节校验。构建报告在 `build_report.json`。

测试经历：全屏启动时原版与测试版均很快退出，切换窗口模式后均可启动至主菜单，日志有 `Load successful`。主菜单按钮为英文图片。自动输入未进入角色创建，不能据此声称中文显示或流程测试通过。

测试中临时将 `d3dparams.ini` 的 StartWindowed 改为 1、`gfx.ini` 的 CreateLogFile 改为 1；两个原始文件保存在本目录且不入库。`restore-settings` 只在当前设置仍与预期测试改动相符时恢复，避免覆盖用户后来修改。

尚需验收：进入角色创建/游戏，检查中文、对话/任务/提示布局，以及存读档；图片菜单另行处理。当前不制作对外发布包。

输入排查（2026-10-13）：重新连接 IDA，确认当前数据库为原始 Inquisitor.exe，SHA-256 与构建基线一致。`0x5674A0` 比较 `menu-newgame_btn`，命中后在 `0x5674E0` 调用 `0x56A780` 切换至 `menu-newgame-dif`；入口来自 `0x570660` 内的 `0x5755D7`。`0x509D80` 在 `0x509DAF` 调用 DirectInput8Create，初始化版本参数为 `0x800`。这些只确认菜单分派及输入技术栈，尚未证明自动点击失效原因；未修改可执行文件或输入逻辑。最新窗口截图仍为主菜单，需要手动点击 NEW GAME 后继续中文显示验收。
