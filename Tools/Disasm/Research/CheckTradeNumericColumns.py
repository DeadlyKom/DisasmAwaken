"""Числовая часть торговой таблицы против независимой модели полей, глифов и выходов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,PC,SP,H,L,D,E
from CheckRowHighlight import make_context
from CheckTextStream import reference as text_reference
from CheckInsetFrame import bitmap_address


def expected(m,index,width,height,origin):
    widths=m[0x8900:0x8A00];columns=(96,114,136,154,176);p=0xEC4C
    for _ in range((index&255)+1):p=m.index(13,p)+1
    positions=[];_,x,_,_,_,_=text_reference(m[p:],widths,0,32,width,height,0,columns,origin,0x20,positions=positions)
    y=32;count=0;market=0x9555+2*index;owned=0x9852+2*index;exit_kind=None
    def glyph(code):
        nonlocal x
        positions.append((code,x,y))
        if y>=height:return 2
        total=x+widths[code]
        if total>255 or total>=width:return 3
        px=origin[0]+x;py=origin[1]+y;x=total
        if py>=185:return 1
        return 0
    def number(value):
        for digit in str(value):
            status=glyph(ord(digit))
            if status:return status
        return 0
    for _ in range(32):
        x=columns[0]
        if m[market]==255:exit_kind='market_ff';break
        count=(count+1)&255
        status=glyph(45) if (m[market]&127)==0 else number(m[market]&127)
        if status in (1,2):exit_kind='market_quantity_vertical';break
        mark=m[market]&128;market+=1
        if mark:x=109;glyph(254)
        x=columns[1];status=number(m[market]);market+=1
        if status in (1,2):exit_kind='market_price_vertical';break
        x=columns[2]
        status=glyph(45) if (m[owned]&127)==0 else number(m[owned]&127)
        if status in (1,2):exit_kind='owned_quantity_vertical';break
        mark=m[owned]&128;owned+=1
        if mark:x=134;glyph(254)
        x=columns[3];status=number(m[owned]);owned+=1
        if status in (1,2):exit_kind='owned_price_vertical';break
        next_y=(y+8)&255
        if next_y>=height:exit_kind='next_row_height';break
        y=next_y
    else:raise AssertionError('Не завершилась независимая таблица')
    image=bytearray(m[0x4000:0x5B00]);accepted=0
    for code,gx,gy in positions:
        if gy>=height or gx+widths[code]>255 or gx+widths[code]>=width:continue
        px=origin[0]+gx;py=origin[1]+gy
        if px>255 or py>184:continue
        for line,bits in enumerate(m[0x8A00+8*code:0x8A08+8*code]):
            for bit in range(8):
                if px+bit<256 and bits&(128>>bit):image[bitmap_address(py+line,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
        accepted+=1
    return image,positions,(x,y),count,market,owned,exit_kind,accepted


def main():
    _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
    initial=get_registers({'SP':0x7FFE,'HL':0,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=accepted=0;kinds={};seen_returns=set();attempts=0
    def execute(stock,owned_stock,index=0,width=200,height=64,origin=(0,0)):
        nonlocal cases,accepted,attempts
        m=bytearray(base);s=Simulator(m);s.registers[:]=initial;r=s.registers;r[H],r[L]=index>>8,index&255;r[PC]=0x7096
        for row in range(30):
            m[0x9555+2*row:0x9557+2*row]=bytes([(row*29+3)%255,(row*73+11)&255])
            m[0x9852+2*row:0x9854+2*row]=bytes([(row*43+5)&255,(row*97+17)&255])
        m[0x9555+60]=255;m[0x9555+2*index]=stock;m[0x9852+2*index]=owned_stock
        for address,value in ((0xBD26,0),(0xAEB3,width),(0xAEAB,height),(0xAEBB,origin[0]),(0xAEBF,0),(0xAEC7,origin[1]),(0xAECB,0),
                              (0xBD73,96),(0xBD7E,114),(0xBD89,136),(0xBD94,154),(0xBD9F,176)):
            m[address]=value
        m[0x4000:0x5B00]=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));m[0x7FFE:0x8000]=bytes([255,63])
        image,positions,cursor,count,market,owned,kind,glyphs=expected(m,index,width,height,origin);calls=[]
        for _ in range(180000):
            pc=r[PC]
            if pc==0x3FFF:break
            if pc==0xAE8D:calls.append((r[A],m[0x6320],m[0x6321]))
            if 0x7096<=pc<0x7154 and m[pc] in (0xC8,0xD0):seen_returns.add(pc)
            s.run()
        else:raise AssertionError(('instruction_limit',stock,owned_stock,index,width,height,origin,hex(r[PC])))
        assert calls==positions,(stock,owned_stock,index,width,height,origin,'glyph_attempts',calls[:12],positions[:12])
        assert m[0x4000:0x5B00]==image,(stock,owned_stock,index,width,height,origin,'bitmap')
        assert (m[0x6320],m[0x6321])==cursor and r[16]==count
        assert (r[D]*256+r[E],r[H]*256+r[L])==(market,owned),(stock,owned_stock,index,width,height,origin,'pointers',r[D]*256+r[E],market,r[H]*256+r[L],owned)
        assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[SP]==0x8000
        # INC FF сохраняет Carry предыдущей проверки строки, остальные биты результата определены.
        if kind=='market_ff':assert r[A]==0 and (r[F]&0xFE)==0x50
        cases+=1;accepted+=glyphs;attempts+=len(calls);kinds[kind]=kinds.get(kind,0)+1
    # Проверка каждого количества и маркера в обоих массивах по отдельности.
    for value in range(256):execute(value,255-value);execute(1,value)
    # Проверка отказов ширины, высоты и физического Y, а также смещённого начала таблиц.
    for index in (0,1,29):
        for width in (95,96,100,109,114,136,154,176,200,255):
            for height in (0,32,33,40,192):
                for origin_y in (0,160,185):execute(128,255,index,width,height,(0,origin_y))
    report=dict(passed=True,cases=cases,independently_composed_glyphs=accepted,glyph_attempts=attempts,exit_kinds=kinds,
                visited_conditional_return_addresses=sorted(seen_returns),all_market_and_owned_quantity_bytes=True,
                glyph_attempts_cursor_count_and_row_pointers_compared=True,whole_bitmap_and_attributes_compared=True,
                real_name_text_numbers_and_glyphs=True,owned_ff_is_not_end_marker=True,
                market_sale_ban_proof_report='OriginalTradeScriptVerification.json',cargo_mark_game_meaning_unknown=True,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/TradeNumericColumnsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
