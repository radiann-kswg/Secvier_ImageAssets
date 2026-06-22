from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
P = Path("proposals2")
DISTAL = Path("/sessions/clever-gallant-knuth/mnt/Secvier_ImageAssets/dist/alphanum")
def font(s):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
    except: return ImageFont.load_default()
CELL=92; PAD=10; LBL=130; HEAD=34

def grid(rows, glyphs, sub, bgc, title, fname):
    cols=len(glyphs)
    W=LBL+cols*(CELL+PAD)+PAD; H=HEAD+len(rows)*(CELL+PAD)+PAD
    s=Image.new("RGB",(W,H),bgc); d=ImageDraw.Draw(s)
    tc=(240,240,240) if sum(bgc)<380 else (20,20,20)
    d.text((PAD,9),title,fill=tc,font=font(19))
    for r,(key,name) in enumerate(rows):
        y=HEAD+r*(CELL+PAD)
        d.text((PAD,y+CELL//2-8),name,fill=tc,font=font(13))
        for ci,g in enumerate(glyphs):
            x=LBL+ci*(CELL+PAD)
            im=Image.open(P/sub/key/"128"/f"{g}.png").convert("RGBA").resize((CELL-10,CELL-10))
            s.paste(im.convert("RGB"),(x+5,y+5),im)
    s.save(fname); print(fname)

ALN=[("seiyuu","星幽 Seiyuu"),("suigyoku","翠玉 Suigyoku"),("kougyoku","紅玉 Kougyoku"),("hakuji","白磁 Hakuji"),("sakin","砂金 Sakin")]
SUI=[("spade","♠ Spade 青"),("heart","♥ Heart 赤"),("diamond","♦ Diamond 金"),("club","♣ Club 緑")]
AG=["char_A","char_R","char_5","char_8"]; SG=["spade","heart","diamond","club"]

grid(ALN,AG,"alphanum",(255,255,255),"alphanum 5 variants — LIGHT","p2_alnum_light.png")
grid(ALN,AG,"alphanum",(24,25,28),"alphanum 5 variants — DARK","p2_alnum_dark.png")
grid(SUI,SG,"suits",(255,255,255),"suits (card 4-color) — LIGHT","p2_suits_light.png")
grid(SUI,SG,"suits",(24,25,28),"suits (card 4-color) — DARK","p2_suits_dark.png")

# harmony: new transparent (on dark) next to existing dist emoji, per variant, char_A
W=4*(CELL+PAD)+PAD+LBL; H=HEAD+len(ALN)*(CELL+PAD)+PAD
s=Image.new("RGB",(W,H),(245,245,245)); d=ImageDraw.Draw(s)
d.text((PAD,9),"既存dist絵文字 vs 新透過(白背/黒背) — char_A",fill=(20,20,20),font=font(15))
for r,(key,name) in enumerate(ALN):
    y=HEAD+r*(CELL+PAD); d.text((PAD,y+CELL//2-8),name,fill=(20,20,20),font=font(12))
    # existing dist emoji
    ex=Image.open(DISTAL/key/"char_A.png").convert("RGBA").resize((CELL-8,CELL-8))
    s.paste(ex.convert("RGB"),(LBL+5,y+5))
    new=Image.open(P/"alphanum"/key/"128"/"char_A.png").convert("RGBA").resize((CELL-10,CELL-10))
    for ci,bgc in enumerate([(255,255,255),(24,25,28)]):
        x=LBL+(ci+1)*(CELL+PAD)
        d.rectangle([x,y,x+CELL,y+CELL],fill=bgc)
        s.paste(new.convert("RGB"),(x+5,y+5),new)
s.save("p2_harmony.png"); print("p2_harmony.png")
