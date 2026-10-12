# 图片文字审查与候选（2026-10-13）

- 来源包：`01_local.dat`；`local/menu/` 下117个资源，其中116个可解码为TGA，另1个实际为ANIM引用文件。
- 36组有字按钮、88个状态已整理；正常/按下/禁用状态均需翻译，不修改箭头、滚动条、数值区域或UI逻辑。
- `attribute_main_menu.tga` 实际为213字节ANIM，引用 `attribute_button_main_lock.tga` 和 `attribute_button_main_normal.tga`，无需当位图编辑。
- `q-game-center.tga` 和 `quit_window.tga` 还有 `QUIT GAME?` 图片文字，需要译为“退出游戏？”。
- 工具：`prepare_ui_atlas.py` 仅打包原始像素到1024×2048参考图集；中文标签映射保存在脚本中。原贴图、元数据、图集在不入库的 `Repack/ui_original/`。
- 使用内置 imagegen、text-localization 模式、透明背景，以参考图集为编辑目标生成候选 `Repack/menu_atlas_ai_candidate_v1.png`。提示要求仅替换为脚本中的36组中文、保留全部88个按钮形状/材质/坐标/透明间隔，正常和按下为象牙色、禁用为灰色，不新增元素。
- 审查结果：**拒绝部署**。图集位置/行距发生变化，部分汉字不准确（如“播放”“返回”等），部分透明边缘有彩色伪影，无法按原坐标可靠拆分。
- 已询问用户是否明确改为程序清除英文并绘制中文，以严格保持像素尺寸、透明通道和状态；未获答复前不执行此编辑方式。
- 启动测试游戏后，自动鼠标输入仍无法进入角色创建。游戏与computer-use进程均为medium integrity，已排除进程权限级别不同；实际中文显示还需游戏内确认。
