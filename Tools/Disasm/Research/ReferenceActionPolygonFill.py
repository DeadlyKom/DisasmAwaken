"""Целочисленный эталон всех записей заполнителя без исполнения Z80."""


def fill(banks, vertices, mode, incoming_hl=0x1357, incoming_sp=0xBFFE):
    ram=[bytearray(b) for b in banks];writes=[]
    def read(a):return ram[2 if a<0xC000 else 0][a&0x3FFF]
    def byte(a,v):
        assert 0x8000<=a<=0xFFFF
        bank=2 if a<0xC000 else 0;v&=255
        ram[bank][a&0x3FFF]=v;writes.append((bank,a&0x3FFF,v))
    def word(a,v):byte(a,v);byte(a+1,v>>8)
    n=len(vertices);low=min(y for y,x in vertices);high=max(y for y,x in vertices)
    word(incoming_sp-2,incoming_hl);byte(0xD3B7,2*n-1)
    if low==high:return ram,writes
    top=next(i for i,(y,x) in enumerate(vertices) if y==low)
    left=right=top
    while vertices[(left-1)%n][0]==low:left=(left-1)%n
    while vertices[(right+1)%n][0]==low:right=(right+1)%n
    byte(0xD4C2,high);byte(0xD4C4,low);byte(0xD387,low)
    word(0xD275,0x9001+2*left);word(0xD3B0,0x9001+2*right)
    pattern,delta=read(0xD100+2*mode),read(0xD101+2*mode)
    byte(0xD1FF,delta);byte(0xD258,delta);word(0xD264,incoming_sp-2)
    byte(0xD22A,low);byte(0xD22C,0x45)
    ix=(((low&7)<<13)+32*vertices[left][1]+2*mode)&65535
    iy=(((low&7)<<13)+32*vertices[right][1]+2*mode+16)&65535
    b=0x80+low//8;left_end=right_end=low
    left_height=right_height=left_sub=right_sub=left_error=right_error=left_step=right_step=0

    def setup(cursor,direction,row,page):
        initial_x=vertices[cursor][1]
        # Поиск восходящего конца с неизменной первоначальной горизонтальной координатой.
        for _ in range(n):
            cursor=(cursor+direction)%n
            if vertices[cursor][0]>row:break
        else:raise AssertionError('конец восходящего ребра отсутствует')
        end_y,end_x=vertices[cursor];height=end_y-row;dx=end_x-initial_x
        magnitude=abs(dx);q,remainder=divmod(magnitude,height)
        step=-((-dx)//height) if dx else 1
        subtract=(0 if magnitude>=height and remainder==0 else height-remainder) if dx>=0 else remainder
        word(0xFFDE,page*256+row)
        is_right=direction>0
        word(0xD3B0 if is_right else 0xD275,0x9001+2*cursor)
        byte(0xD223 if is_right else 0xD217,height)
        byte(0xD387 if is_right else 0xD4C4,end_y)
        byte(0xD21F if is_right else 0xD213,subtract)
        return cursor,end_y,height,subtract,height//2,(0x2000+32*step)&65535

    for row in range(low,high):
        page=0x8C+((row-low)&1)
        # Подготовка рёбер происходит до рисования строки, левая цепочка имеет приоритет при равенстве.
        if row>=left_end:
            left,left_end,left_height,left_sub,left_error,left_step=setup(left,-1,row,page)
            if row>=right_end:
                byte(0xD22A,right_end);byte(0xD22C,0x3B)
            else:
                limit=min(high,left_end,right_end)
                branch=0x3B if right_end<min(left_end,high) else 0x45 if left_end<high else 0x36
                byte(0xD22A,limit);byte(0xD22C,branch)
        if row>=right_end:
            right,right_end,right_height,right_sub,right_error,right_step=setup(right,1,row,page)
            limit=min(high,left_end,right_end)
            branch=0x3B if right_end<min(left_end,high) else 0x45 if left_end<high else 0x36
            byte(0xD22A,limit);byte(0xD22C,branch)
        c_left,c_right=ix>>8,iy>>8
        left_address=(b<<8)|c_left;right_address=(b<<8)|c_right
        mask_left=page*256+(ix&255);mask_right=page*256+(iy&255)
        # Формирование двух крайних масок либо их объединения при одном байте строки.
        if c_left<c_right:
            difference=c_right-c_left;byte(0xD244,(-2*difference)&255)
            byte(left_address,(read(left_address)&read(mask_left))|read(mask_left+1))
            for column in range(c_left+1,c_right):byte((b<<8)|column,pattern)
            byte(right_address,(read(right_address)&read(mask_right))|read(mask_right+1))
        elif c_left==c_right:
            preserve=read(mask_left)|read(mask_right)
            byte(left_address,(read(left_address)&preserve)|((255^preserve)&read(mask_right+1)))
        pattern^=delta
        # Продвижение упакованных границ, перенос IX учитывается до дробной коррекции.
        total=ix+left_step
        if total>65535:b=(b+1)&255
        ix=total&65535;left_error-=left_sub
        if left_error<0:left_error+=left_height;ix=(ix-32)&65535
        iy=(iy+right_step)&65535;right_error-=right_sub
        if right_error<0:right_error+=right_height;iy=(iy-32)&65535
    return ram,writes
