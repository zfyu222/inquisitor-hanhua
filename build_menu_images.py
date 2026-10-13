"""Generate reviewed Chinese menu sprites, without changing the installed game."""
import json
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]/'Tools/localization'))
from sprite_text import replace_text

FONT = Path('C:/Windows/Fonts/simsun.ttc')
WORK = ROOT/'Repack'
OUTPUT = WORK/'ui_translated'


def main():
    tiles = json.loads((WORK/'ui_original/menu_atlas_manifest.json').read_text(encoding='utf-8'))
    report = []
    atlas = Image.new('RGBA', (1024,2048))
    for tile in tiles:
        source = Path(tile['source'])
        width,height = Image.open(source).size
        box = (26, 5, width-22, height-5)
        if tile['base'] == 'act_ok': box = (54, 7, 116, 36)
        if tile['base'] == 'exit': box = (22, 6, 96, 34)
        if tile['base'] == 'automap_back': box = (43, 13, 132, 40)
        if tile['base'].startswith('q-game-butt'): box = (28, 4, 72, 25)
        if tile['base'] == 'options_default': box = (14, 5, width-12, height-5)
        color = (154,150,136) if tile['state'] == 'unuse' else (239,224,174)
        if tile['base'].startswith('select_') and tile['state'] == 'normal': color = (182,175,148)
        threshold = 100 if tile['state'] == 'unuse' else 150
        if tile['base'].startswith('select_') and tile['state'] == 'normal': threshold = 115
        data, item = replace_text(source,tile['label'],box,FONT,23,color,threshold)
        path = OUTPUT/tile['path']
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        item.update(path=tile['path'],state=tile['state'])
        report.append(item)
        atlas.paste(Image.open(path).convert('RGBA'), tuple(tile['box'][:2]))
    for name,box,background in [('q-game-center.tga',(77,27,286,64),(77,78,286,115)),('quit_window.tga',(85,69,296,107),(85,114,296,152))]:
        source = WORK/'ui_original/01_local/local/menu'/name
        data,item = replace_text(source,'退出游戏？',box,FONT,30,(238,189,128),-1,background)
        path = OUTPUT/'local/menu'/name
        path.write_bytes(data)
        Image.open(path).save(WORK/(name+'.preview.png'))
        item.update(path='local/menu/'+name,state='title')
        report.append(item)
    atlas.save(WORK/'menu_atlas_zh.png')
    (WORK/'menu_build_report.json').write_text(json.dumps(dict(font=str(FONT),resources=report,
        count=len(report),review='Pending visual review; not deployed by this script'),ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Generated {len(report)} sprites; preserved dimensions, TGA headers, alpha and pixels outside text boxes.')

if __name__ == '__main__': main()
