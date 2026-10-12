"""Pack original menu sprites into one editable atlas without changing their pixels."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
WORK = ROOT/'Repack/ui_original'
LABELS = {
    'act_ok': '确定', 'attribute_button_main': '主菜单', 'attribute_button_start': '开始游戏',
    'audio': '音频', 'automap_back': '返回', 'cinematics': '过场动画', 'controls': '操作',
    'credits': '制作人员', 'easy': '简单', 'exit': '退出', 'game_delete': '删除',
    'game_load': '读取', 'game_no': '否', 'game_save': '保存', 'game_yes': '是', 'hard': '困难',
    'load': '读取存档', 'medium': '普通', 'multiplayer': '多人游戏', 'new_game': '新游戏',
    'options_back': '返回', 'options_cinematics_back': '返回', 'options_cinematics_play': '播放',
    'options_default': '默认', 'options': '设置', 'options_ok': '确定',
    'q-game-butt-no': '否', 'q-game-butt-yes': '是', 'resume': '继续游戏', 'save': '保存游戏',
    'select_back': '返回', 'select_paladin': '圣骑士', 'select_priest': '牧师',
    'select_thief': '盗贼', 'singleplayer': '单人游戏', 'video': '视频',
}

def main():
    atlas = Image.new('RGBA', (1024,2048), (0,0,0,0))
    tiles = []
    for row, (base, label) in enumerate(LABELS.items()):
        for column, state in enumerate(['normal','lock','unuse']):
            separator = '-' if base.startswith('q-game-') else '_'
            relative = f'local/menu/{base}{separator}{state}.tga'
            path = WORK/'01_local'/relative
            if not path.exists():
                continue
            image = Image.open(path).convert('RGBA')
            x,y = column*320+20, row*54+10
            assert image.width <= 280 and image.height <= 54
            atlas.paste(image,(x,y))
            tiles.append(dict(path=relative,base=base,state=state,label=label,row=row+1,
                              box=[x,y,x+image.width,y+image.height],source= str(path)))
    atlas.save(WORK/'menu_atlas_original.png')
    (WORK/'menu_atlas_manifest.json').write_text(json.dumps(tiles,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Rows:',len(LABELS),'Sprites:',len(tiles))

if __name__ == '__main__':
    main()
