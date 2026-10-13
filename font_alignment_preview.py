"""Preview actual BFI/bitmap glyphs from two overlay files, at engine positions."""
import argparse
import io
import re
from pathlib import Path
from PIL import Image, ImageDraw
from drpk_extract import entries, expand

TEXT = '一二三国，天地。你好——你好……你好！'

def load(path):
    return {name:expand(content,size) for name,size,packed,offset,content in entries(path)
            if name.lower().startswith('local/fnt/')}

def render(resources, name):
    bfi = resources[f'local/fnt/{name}.bfi'].decode('utf-16')
    bitmap_name = 'NosferatuS' if name == 'NosferatuSBlack' else name
    atlas = Image.open(io.BytesIO(resources[f'local/fnt/{bitmap_name}.bmp'])).convert('RGB')
    glyphs = {}
    for line in bfi.splitlines():
        if line.startswith('Character='):
            fields = dict(re.findall(r'(\w+)=(-?[0-9.]+)',line))
            glyphs[line[11]] = {k:float(v) for k,v in fields.items()}
    canvas = Image.new('RGB',(500,36))
    cursor = 4
    for char in TEXT:
        f = glyphs[char]
        box = tuple(round(f[k]*d) for k,d in [('u1',atlas.width),('v1',atlas.height),('u2',atlas.width),('v2',atlas.height)])
        glyph = atlas.crop(box)
        canvas.paste(glyph,(cursor+round(f['ScreenRectLeft']),4+round(f['ScreenRectTop'])))
        cursor += round(f['WidthA']+f['WidthB']+f['WidthC'])
    return canvas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('before',type=Path)
    parser.add_argument('after',type=Path)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    before,after = load(args.before),load(args.after)
    canvas = Image.new('RGB',(1000,160),(30,30,30))
    draw = ImageDraw.Draw(canvas)
    for row,name in enumerate(['Nosferatu','NosferatuS']):
        draw.text((4,row*80+2),name+' BEFORE',fill='white')
        draw.text((504,row*80+2),name+' AFTER',fill='white')
        canvas.paste(render(before,name),(0,row*80+18))
        canvas.paste(render(after,name),(500,row*80+18))
    canvas.resize((2000,320),Image.Resampling.NEAREST).save(args.output)

if __name__ == '__main__':main()
