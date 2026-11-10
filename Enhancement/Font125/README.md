# 字体125%增强

为 Steam Windows Build 6307888 + 子非鱼汉化 v1.0 制作的可选叠加包。

## 产物与使用

- ZIP：`Inquisitor_独立增强补丁_字体125.zip`。
- 解压前目录：`Files/`，其中 `Game/04_enhancement_font125.dat` 是唯一游戏载荷。
- 在工程内双击 `Files/安装字体125.cmd` 安装，双击 `Files/卸载字体增强.cmd` 恢复100%。脚本也可随ZIP解压到游戏根目录使用。
- 命令行支持 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File Files/manage.ps1 -Action install -GameRoot "游戏根目录"`，卸载用 `-Action uninstall`。
- 安装依赖汉化v1.0；“独立”指单独的可选包，不能替代汉化本体。开发交付仅在本工程生成，没有安装到实际游戏或公开发布。

## 实现

从经过SHA-256校验的汉化v1.0载荷读取 Nosferatu、NosferatuS、NosferatuSBlack 三套BFI。
每套只将 `TextScaleX` / `TextScaleY` 从 `1.0` 改为 `1.25`，共6处修改。
继承汉化字库位图与基线；引擎使用同一缩放参数处理屏幕矩形、字宽、折行测量及行距。
新DAT在03_zh.dat之后加载，仅包含3份BFI，不重打包译文、菜单和位图。

## 构建与验证

在此目录运行 `python build.py`；依赖项目现有DRPK构建/解码程序、Pillow和fontTools，以及工作区QuickBMS 0.12.0。
原生分析使用REA 6.4.0 + Ghidra 12.1.4，证据在 `../../Analysis/font125/`。
构建校验严格限制只有两个缩放字段改变；3份资源通过项目解码和QuickBMS独立解码逐字节对照；ZIP CRC和载荷哈希校验通过。
在隔离的游戏文件副本上通过9项安装检查：安装、重复安装、卸载、重复卸载、拒绝改动未知增强文件、缺少汉化时拒绝安装、解压目录内安装与卸载。记录见 `installer_verification.json`；实际游戏文件未改动。
`preview.png` 是从实际BFI/字库生成的离线模拟对照，不是游戏截图，也不替代实机验证。

## 范围与待测

- 动态字体的中文、拉丁字母、数字及同字库符号统一缩放；菜单图片文字不在本功能范围内。
- 这是原位图的引擎缩放，非重新绘制更高分辨率的字库。
- 字体变大后同一文本框可容纳的字数减少。对话、任务、属性、物品提示等固定区域的截断/溢出尚未实机确认。
- 沿用项目此前停止进一步游戏测试的安排，本次只做离线校验；不宣称实机排版通过。
- 安装脚本只接受已知EXE和汉化载荷；遇到未知同名增强文件会停止。卸载仅移除哈希匹配的增强DAT，保留汉化。
