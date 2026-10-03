"""Developer utility: original illustrative fixtures, no real user/platform material.
Requires Pillow only when regenerating these committed test images.
"""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

def create(output, font_path):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    def font(size):return ImageFont.truetype(str(font_path),size)
    for number in range(1,4):
        image=Image.new('RGB',(780,980),'#f2eee4');d=ImageDraw.Draw(image)
        d.text((40,28),'原创合成演示 · 非真实笔记',font=font(22),fill='#5f6960')
        titles=[('租房台面总是挤？','先把杯子立起来'),('先量台面，再放杯架','别挡住水槽的操作区'),('看得见的变化','不是效果保证')]
        d.text((40,90),titles[number-1][0],font=font(43),fill='#223f37')
        d.text((40,158),titles[number-1][1],font=font(38),fill='#223f37')
        d.rounded_rectangle((38,270,742,740),radius=16,fill='#e1dbc9')
        d.rectangle((38,640,742,740),fill='#c0b494')
        d.rounded_rectangle((280,405,665,620),radius=18,fill='#608b73',outline='#2d5741',width=4)
        d.rectangle((302,580,642,625),fill='#365f49')
        for x,y in [(325,475),(440,475),(555,475)]:
            d.rounded_rectangle((x,y,x+68,y+95),radius=10,fill='#fffaf0',outline='#526d58',width=3)
            d.arc((x+55,y+20,x+90,y+65),270,90,fill='#fffaf0',width=9)
        d.rectangle((100,635,190,680),fill='#54776e')
        if number==1:
            d.rounded_rectangle((44,778,330,853),radius=9,fill='#244f3e');d.text((65,786),'示例价 19.9元',font=font(30),fill='white')
            d.text((45,880),'折叠杯架｜插画演示，不代表实拍',font=font(24),fill='#48564d')
        elif number==2:
            d.line((250,370,680,370),fill='#345341',width=4)
            d.text((270,315),'摆放位置示意',font=font(26),fill='#345341')
            d.text((45,780),'使用顺序：量尺寸 → 放架 → 摆杯',font=font(29),fill='#345341')
            d.text((45,855),'需核对尺寸；演示未进行承重测试',font=font(24),fill='#5f5143')
        else:
            d.text((45,777),'作者式表达示例：台面更好整理',font=font(28),fill='#345341')
            d.text((45,838),'限制：只展示摆放，不证明耐用性',font=font(24),fill='#5f5143')
            d.text((45,898),'先量尺寸，再考虑是否适合自己',font=font(25),fill='#345341')
        image.save(output/f'image-{number:02d}.png',optimize=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--font',required=True);a=p.parse_args();create(a.output,a.font)
