"""D314, независимое состояние радиуса/ошибки, две фазы рисования и непиксельные записи."""
from CheckControlsCircleSpan import add_flags
from ReferenceControlsPointRespawn import cp_flags

LAYOUTS={
    None:dict(slow_odd=0xD672,fast_odd=0xD705,fast_jump=0xD716,fill_return=0xD676,slow_up=0xD67B,slow_down=0xD681,fast_up=0xD734,fast_down=0xD739),
    'left':dict(slow_odd=0xD772,fast_odd=0xD7FD,fast_jump=0xD80E,fill_return=0xD776,slow_up=0xD77B,slow_down=0xD780,fast_up=0xD82C,fast_down=0xD831),
    'right':dict(slow_odd=0xD86C,fast_odd=0xD8EF,fast_jump=0xD900,fill_return=0xD870,slow_up=0xD877,slow_down=0xD87C,fast_up=0xD91E,fast_down=0xD923)}


def evaluate(registers,cx,cy,radius,half_parameters=None):
    r=list(registers);stack=r[12];writes=[];paths=[]
    toggle,fill=r[8:10];left,right=cx-radius,cx+radius
    initial_clip=half_parameters[2] if half_parameters is not None and len(half_parameters)>2 else None
    virtual_left=half_parameters is not None and len(half_parameters)>3 and half_parameters[3]
    if initial_clip=='left' or virtual_left:left=8
    if initial_clip=='right':right=248
    left_mask=(255<<(7-(left&7)))&255;right_mask=255>>(right&7)
    if initial_clip=='left' or virtual_left:left_mask=0
    if initial_clip=='right':right_mask=255
    left_address=0x8000+32*cy+left//8;right_address=0x8000+32*cy+right//8

    def put(address,value):writes.append((address,value))
    def word(address,value):put(address,value&255);put(address+1,(value>>8)&255)
    def build(return_address):
        # Создание реальной рамки BuildCircleSpan и сохранение маски первого края.
        word(stack-2,return_address);word(stack-4,0xD335)
        word(stack-4,(right<<8)|add_flags(cx,radius));put(0xD18A,left_mask)

    def half(direction,saved_sp):
        nonlocal fill
        error=0;x=radius;alt_y=0 if half_parameters is None else half_parameters[1]
        h=right_address>>8;l=right_address&255;e=left_address&255
        b,c=left_mask,right_mask;d=radius if half_parameters is None else r[4];y=0;row_count=0
        clip=initial_clip;af_prime=list(r[16:18]);swapped=False;transitions=0;exit_reason=None
        saved_af=(left_mask<<8)|0x42 if half_parameters is None else r[0]*256+r[1]
        word(saved_sp,saved_af);put(0xD18B,int(direction>0))
        if clip is None and e==l:
            paths.append(dict(direction=direction,reason='byte_convergence_initial',rows=0,error=0,x=x,alt_y=alt_y))
            return h,l,d,e,b,c,error,x,alt_y,swapped,af_prime
        word(0xD186,saved_sp)

        def draw(fast):
            nonlocal d,row_count
            layout=LAYOUTS[clip];d=l;between=d-e-int(clip!='left');assert 0<=between<32
            count=between//2
            if between&1:put(layout['fast_odd' if fast else 'slow_odd'],count)
            # Записи CPU-стека и изменяемых смещений отделены от независимого пиксельного оракула.
            if fast:
                put(layout['fast_jump'],16-count)
                word(saved_sp-2,(d<<8)|e);word(saved_sp-4,(fill<<8)|fill)
                continuation=layout['fast_down' if direction>0 else 'fast_up']
            else:
                word(saved_sp-2,layout['fill_return'])
                if count:
                    word(saved_sp-4,(h<<8)|d);put(0xCEB4,62-4*count)
                continuation=layout['slow_down' if direction>0 else 'slow_up']
            word(saved_sp-2,continuation);row_count+=1

        def advance():
            nonlocal fill,y,h,l,e
            fill^=toggle;y+=1;row=cy+direction*y
            pointer=((h<<8)|l)+direction*32;h,l=(pointer>>8)&255,pointer&255;e=(e+direction*32)&255
            return 0<=row<96

        def shrink(fast):
            nonlocal b,c,e,l,error,x,clip,swapped,transitions,exit_reason,af_prime
            # Сужение двух открытых границ на один пиксель, совпадение байтов прекращает проход до обновления ошибки.
            if clip!='left':
                carry=b&1;b=(b>>1)|128
                if carry:
                    e=(e+1)&255
                    if e==l:return False
                    b=128
            if clip!='right':
                carry=c>>7;c=((c<<1)|1)&255
                if carry:
                    l=(l-1)&255
                    if (e==l if clip is None else ((l-e+1)&255)==0):return False
                    c=1
            error=((error-x+32768)&65535)-32768
            counter=(((-x)&255)+1)&255;x=256-counter
            # Исходный быстрый выход проверяет оборачивание C' до второго прибавления и до обратного EXX.
            if fast and counter==0:
                swapped=True;exit_reason='counter_wrap_fast';return False
            if clip is not None:
                af_prime[1]=cp_flags(af_prime[0],counter)
                if af_prime[0]==counter:
                    previous=clip;clip=None;transitions+=1
                    if previous=='left' and l==e:
                        swapped=True;exit_reason='left_transition_same_byte';return False
            error=((error-x+32768)&65535)-32768
            return True

        def advance_difference():
            nonlocal error,alt_y
            # Расчёт двух прибавлений байтового E', его переход FF в 00 не переносится в D'.
            previous=alt_y;alt_y=(alt_y+1)&255
            error=((error+previous+alt_y+32768)&65535)-32768

        draw(False)
        if not advance():reason='vertical'
        else:
            fast=False
            for _ in range(2048):
                if not fast:
                    # Вертикальная фаза обновляет разность квадратов после перехода строки.
                    advance_difference()
                    if error<0:
                        draw(False)
                        if not advance():reason='vertical';break
                        continue
                    if not shrink(False):reason=exit_reason or 'byte_convergence';break
                    if error<0:
                        draw(False)
                        if not advance():reason='vertical';break
                        continue
                    fast=True
                # Горизонтальная фаза сужает границы до отрицательной ошибки, затем готовит следующую разность до PUSH-рисования.
                if not shrink(True):reason=exit_reason or 'byte_convergence';break
                if error>=0:continue
                advance_difference()
                draw(True)
                if not advance():reason='vertical';break
            else:raise AssertionError('незавершённый контур')
        paths.append(dict(direction=direction,reason=reason,rows=row_count,error=error,x=x,alt_y=alt_y,transitions=transitions,register_sets_swapped=swapped))
        return h,l,d,e,b,c,error,x,alt_y,swapped,af_prime

    if half_parameters is None:
        build(0xD317);word(stack-2,0xD31A);half(-1,stack-4)
        build(0xD31D);state=half(1,stack-2)
    else:state=half(half_parameters[0],stack-2)
    h,l,d,e,b,c,error,x,alt_y,swapped,af_prime=state
    r[0:8]=[left_mask,0x42,b,c,d,e,h,l] if half_parameters is None else [r[0],r[1],b,c,d,e,h,l]
    r[9]=fill
    r[18:24]=[255,(-x)&255,0,alt_y,(error&65535)>>8,error&255]
    if swapped:r[2:8],r[18:24]=r[18:24],r[2:8]
    r[16:18]=af_prime
    r[12],r[24]=stack+2,0x3FFF
    return dict(registers=r,writes=writes,paths=paths)


def evaluate_half(registers,cx,cy,x,initial_y,direction):
    return evaluate(registers,cx,cy,x,half_parameters=(direction,initial_y))


def evaluate_clipped_half(registers,curve_x,cy,x,initial_y,direction,clip,virtual_left=False):
    assert clip in ('left','right')
    cx=curve_x-x if clip=='left' else curve_x+x
    return evaluate(registers,cx,cy,x,half_parameters=(direction,initial_y,clip,virtual_left))
