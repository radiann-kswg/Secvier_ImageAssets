from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P = Path("proposals")
VARIANTS = [("jisetsu","磁雪 Jisetsu"),("shitsuboku","漆墨 Shitsuboku"),
            ("suigyoku","翠玉 Suigyoku"),("sakin","砂金 Sakin")]
GLYPHS = ["char_A","char_R","char_5","char_8","spade","heart","diamond","club"]
# background strips emulate light/dark chat surfaces
BGS = [("Light #FFFFFF",(255,255,255)),("Light #F0F0F2",(240,240,242)),
       ("Gray #8A8A8A",(138,138,138)),("Dark #1E1F22",(30,31,34)),
       ("Dark #000000",(0,0,0)),("Brand #5865F2",(88,101,242))]
def font(sz):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(p, sz)
        except: pass
    return ImageFont.load_default()
CELL=96; PAD=10; LBLW=150; HEAD=34
cols=len(GLYPHS); 
# one big sheet per variant: rows=bg, cols=glyph
for key,name in VARIANTS:
    W = LBLW + cols*(CELL+PAD) + PAD
    H = HEAD + len(BGS)*(CELL+PAD) + PAD
    sheet = Image.new("RGB",(W,H),(250,250,250))
    d = ImageDraw.Draw(sheet)
    d.text((PAD,8), name, fill=(20,20,20), font=font(22))
    for r,(bgn,bgc) in enumerate(BGS):
        y = HEAD + r*(CELL+PAD)
        d.rectangle([LBLW-4,y,W-PAD,y+CELL], fill=bgc)
        d.text((PAD,y+CELL//2-8), bgn, fill=(20,20,20), font=font(13))
        for cidx,g in enumerate(GLYPHS):
            x = LBLW + cidx*(CELL+PAD)
            im = Image.open(P/key/"128"/f"{g}.png").convert("RGBA").resize((CELL-12,CELL-12))
            tile = Image.new("RGBA",(CELL,CELL),bgc+(255,))
            tile.alpha_composite(im,(6,6))
            sheet.paste(tile.convert("RGB"),(x,y))
    sheet.save(f"preview_{key}.png")
    print("saved preview_"+key)

# combined master grid: all variants, on white & black, one glyph row
def strip(bgc, fname):
    rows=VARIANTS
    W = LBLW + cols*(CELL+PAD)+PAD; H = HEAD+len(rows)*(CELL+PAD)+PAD
    sheet=Image.new("RGB",(W,H),bgc); d=ImageDraw.Draw(sheet)
    tcol=(245,245,245) if sum(bgc)<380 else (20,20,20)
    d.text((PAD,8),f"All variants on {fname}",fill=tcol,font=font(20))
    for r,(key,name) in enumerate(rows):
        y=HEAD+r*(CELL+PAD)
        d.text((PAD,y+CELL//2-8),name,fill=tcol,font=font(13))
        for cidx,g in enumerate(GLYPHS):
            x=LBLW+cidx*(CELL+PAD)
            im=Image.open(P/key/"128"/f"{g}.png").convert("RGBA").resize((CELL-12,CELL-12))
            sheet.paste(im.convert("RGB"),(x+6,y+6),im)
    sheet.save(fname); print("saved",fname)
strip((255,255,255),"preview_ALL_light.png")
strip((24,25,28),"preview_ALL_dark.png")
