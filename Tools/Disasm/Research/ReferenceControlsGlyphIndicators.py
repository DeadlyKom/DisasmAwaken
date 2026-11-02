"""Независимые координатные ограничения, очистка зон и OR трёх знаков E021."""
from CheckControlsThreeRowGlyph import next_scanline
from CheckControlsCircleSpan import add_flags
from CheckControlsEvenSpan import and_flags


def clamp_axis(value,center,lower,upper,check_overflow):
    expanded = (value+center)&255
    overflow = bool(add_flags(value,center)&4) if check_overflow else False
    if overflow:
        expanded = lower
    under = expanded<lower
    if under:
        expanded = lower
    over = expanded>=upper
    if over:
        expanded = upper-1
    return expanded,(8 if check_overflow else 7)+int(overflow)+int(under)+int(over)


def reference(memory,initial,mode,gate,first,second,third):
    result = list(initial)
    result[6:8] = [0,0]
    writes = [(0xE089,initial[12]&255),(0xE08A,initial[12]>>8)]
    # Очистка четырёх столбцов, промежуточный столбец и соседняя правая область сохраняются.
    for low in (0xB8,0xD8):
        for high in range(0x48,0x50):
            top = (high<<8)|low
            writes += [(top-1,0),(top-2,0),(top-4,0),(top-5,0)]
    for address,value in writes:
        memory[address] = value
    cost = 71
    glyph_count = 0

    def draw(vector,which):
        nonlocal cost,glyph_count,result
        vx,vy,sign = vector
        center,lower,upper = (0xB8,0xB0,0xBE) if which==2 else (0xA0,0x98,0xA6)
        x,cost_x = clamp_axis(vx,center,lower,upper,True)
        y,cost_y = clamp_axis(vy,0x70,0x68,0x76,False)
        negative = bool(sign&128)
        base = (0xE1E1 if negative else 0xE1B1) if which==0 else (0xE241 if negative else 0xE211)
        phase = x&7
        source = base+6*phase
        address = 0x4000|((y&0xC0)<<5)|((y&7)<<8)|((y&0x38)<<2)|(x>>3)
        if which<2:
            returned = 0xE0CA if which==0 else 0xE113
            writes.extend(((initial[12]-1,returned>>8),(initial[12]-2,returned&255)))
            memory[initial[12]-1],memory[initial[12]-2] = returned>>8,returned&255
        for row in range(3):
            for column in range(2):
                target = (address&0xFF00)|((address+column)&255)
                value = memory[target]|memory[source+2*row+column]
                memory[target] = value
                writes.append((target,value))
            if row<2:
                address,_,_ = next_scanline(address)
        final = (address&0xFF00)|((address+1)&255)
        value = memory[final]
        flags = (value&0xA8)|(0x40 if value==0 else 0)|(4 if value.bit_count()%2==0 else 0)
        result[0:8] = [value,flags,y,2*phase,(source+5)>>8,(source+5)&255,final>>8,final&255]
        glyph_cost = 69 if y&7<6 else 73 if y&63>=62 else 76
        cost += cost_x+cost_y+4+int(negative)+int(which<2)+glyph_cost
        glyph_count += 1

    if mode!=1:
        draw(first,0)
    # Проверка всего OR-вектора, C получает только OR первых двух байтов до добавления знакового байта.
    result[3] = second[0]|second[1]
    sentinel = result[3]|second[2]
    cost += 9
    if sentinel==0x80:
        result[0:2] = [0x80,0x42]
        route = 'second_sentinel'
    else:
        draw(second,1)
        cost += 3
        if gate:
            result[0:2] = [gate,and_flags(gate)]
            route = 'third_gate'
        else:
            draw(third,2)
            route = 'third_tail'
    return result,writes,cost,route,glyph_count
