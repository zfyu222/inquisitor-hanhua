# 字体125%分析证据（2026-11-10）

- 工具：REA 6.4.0，显式 `provider_id=ghidra`，Ghidra 12.1.4；只读分析，已关闭会话。
- 输入：`D:/Program Files (x86)/Steam/steamapps/common/Inquisitor/Game/Inquisitor.exe`（真实NTFS路径，非工程junction）。
- EXE SHA-256：`88854166fe459cb1937b075604d906c88c3e1109d7b87fb17cb494939c7a9276`；离线安装测试前后再次核对不变。
- PE映像基址 `0x400000`；本目录函数标记是虚拟地址，不是文件偏移。本功能不修改EXE。
- 复现调用：`open_binary(path=<上述路径>,provider_id=ghidra)` → `procedure_pseudo_code(procedure=<函数VA>)` / `procedure_assembly(procedure=<函数VA>)` → `close_binary()`。

## 结论

- `0x411c80`：BFI加载器将 `TextScaleX=%f` 写入字体对象 `+0x28`，`TextScaleY=%f` 写入 `+0x2c`；FontSize在`+0x30`，LineGap在`+0x34`。
- `0x412620`：字形绘制在`0x412794/0x4127ed`以X缩放乘屏幕横坐标，`0x4127c1/0x41280c`以Y缩放乘屏幕纵坐标，`0x412933`以X缩放乘光标前进量。
- `0x412950`：多行绘制使用 `LineGap * TextScaleY`，并以 `TextScaleX` 累积字宽再决定折行。
- `0x412d40`：Ghidra伪代码遗漏部分x87浮点数据流，不能单凭伪代码判断未缩放。汇编`0x412df7–0x412dfe`计算 `LineGap * TextScaleY`；`0x412f1b/0x412f56`缩放横向边界，`0x412f75/0x412fa0`缩放纵向边界，`0x412ffe`缩放前进量。绘制与测量使用一致的缩放参数。
- 因此只修改三套BFI的两个浮点字段，保持字形、UV、位图、整数度量与行距原值，不进行二次缩放。

## 限制

这些是静态调用链证据。局部UI是否在其他位置另设固定边界、文字变大后能否完整显示，需要具体场景实机检查。没有启动游戏，也未验证增强包实际加载及所有界面排版。
DRPK加载顺序复用项目既有 `Repack/analysis_notes.md` 中已验证的命名覆盖规则，新命名 `04_enhancement_font125.dat` 排在汉化 `03_zh.dat` 之后。
