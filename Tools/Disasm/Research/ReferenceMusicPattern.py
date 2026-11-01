"""Независимая семантика команд строки PT3 этой версии, не интерпретатор Z80."""
PROFILES = {
    'A': dict(entry=0xE439, pending=0xDE4D, current=0xE0BB, volume=0xDE5D, enable=0xDE48,
              sample=0xDE52, ornament=0xDE68, envelope=0xDE6E, row_delay=0xDFC9,
              effect_page=0xDD, effect_anchor=0xDE, delay=0xDE7A, step=0xDE82,
              branch=0xDE88, target=0xDE75, sample_pos=0xDEA6, sample_gate=0xDEA3,
              orn_pos=0xDEB1, orn_gate=0xDEAE, on=0xDE97, off=0xDE9F, gate=0xDE90),
    'B': dict(entry=0xE4E6, pending=0xDEDB, current=0xE1BB, volume=0xDEEB, enable=0xDED6,
              sample=0xDEE0, ornament=0xDEF6, envelope=0xDEFC, row_delay=0xE39F,
              effect_page=0xDD, effect_anchor=0xFE, delay=0xDF08, step=0xDF10,
              branch=0xDF16, target=0xDF03, sample_pos=0xDF34, sample_gate=0xDF31,
              orn_pos=0xDF3F, orn_gate=0xDF3C, on=0xDF25, off=0xDF2D, gate=0xDF1E),
    'C': dict(entry=0xE583, pending=0xE2B9, current=0xE6EC, volume=0xE22B,
              sample=0xE1F5, ornament=0xE276, envelope=0xE235, row_delay=0xE3D0,
              effect_page=0xDE, effect_anchor=0x1E, delay=0xE29D, reload=0xE2CC,
              step=0xE2A6, branch=0xE2AD, target=0xE2B1,
              sample_pos=0xE1F9, orn_pos=0xE27A, on=0xE2E7, off=0xE2E3, counter=0xE2D5)}
HANDLERS = {'A': {1: 0xE60C, 2: 0xE623, 3: 0xE647, 4: 0xE652, 5: 0xDDCA, 8: 0xDB8C, 9: 0xE6FA},
            'B': {1: 0xE65D, 2: 0xE674, 3: 0xE698, 4: 0xE6A3, 5: 0xDDEA, 8: 0xDB8C, 9: 0xE6FA},
            'C': {1: 0xE6AE, 2: 0xE6C9, 3: 0xE6EE, 4: 0xE6F4, 5: 0xDE0A, 8: 0xDB8C, 9: 0xE6FA}}


def decode(source, channel, de=0x7000, hl=0xDB57, alternate=None, stack=0xBFFE):
    p = PROFILES[channel]
    m = list(source)
    writes, effects, commands = [], [], []
    alt = list(alternate or [0xDE, 0xF0, 0x9A, 0xBC, 6, 0x18, 0x12, 0x34])
    sp = stack
    a = f = 0
    bc = 0x1020

    def put(address, value):
        m[address] = value
        writes.append((address, value))

    def word(address, value):
        put(address, value & 255)
        put(address + 1, value >> 8)

    def take():
        nonlocal de
        value = m[de]
        de = (de + 1) & 65535
        return value

    def take_word():
        low = take()
        return low + 256 * take()

    def pointer(low, destination):
        nonlocal hl, bc
        # Расчёт адреса в текущей странице H, INC L не переносит единицу в H.
        address = (hl & 0xFF00) | (low & 255)
        following = (address & 0xFF00) | ((address + 1) & 255)
        bc = m[address] + 256 * m[following]
        hl = following
        word(destination, bc)

    def envelope(mask, reset=False):
        put(p['envelope'], mask)
        if channel != 'C':
            alt[2] = alt[4]
        elif reset:
            put(p['orn_pos'], 0)

    def period(shape):
        put(0xDF48, shape)
        put(0xDF51, take())
        put(0xDF50, take())

    for _ in range(128):
        op = take()
        commands.append(op)
        if op >= 0xF0:
            pointer(0xE0 + 2 * (op - 0xF0), p['ornament'])
            envelope(0, True)
            pointer(0xA0 + take(), p['sample'])
        elif op >= 0xD0:
            if op == 0xD0:
                a, f = 0, 0x41
                break
            pointer(0xA0 + 2 * (op - 0xD0), p['sample'])
        elif op >= 0xC0:
            if op == 0xC0:
                if channel == 'C':
                    put(p['counter'], 0)
                    put(0xE1EE, 255)
                    a, f = 255, 0xBB
                else:
                    put(p['enable'], 0x2F)
                    alt[6] = alt[4]
                    a, f = 0x2F, 0x41
                break
            put(p['volume'], (op - 0xC0) * 16)
            continue
        elif op >= 0xB0:
            if op == 0xB1:
                put(p['row_delay'], take())
            else:
                mask = 0
                if op != 0xB0:
                    period(op - 0xB1)
                    mask = 0x10
                envelope(mask)
            continue
        elif op >= 0x50:
            put(p['pending'], op - 0x50)
            if channel == 'C':
                for address in (0xE1F9, 0xE23C, 0xE253, 0xE27A, 0xE29D, 0xE1EE, 0xE2D5):
                    put(address, 0)
                word(0xE26A, 0)
                put(0xE20F, 0x10)
                hl, a, f = 0, 0x10, 0x44
            else:
                put(p['enable'], 0)
                alt[6] = alt[4]
                a, f = 0, 0x44
            bc = 0x0120
            break
        elif op >= 0x40:
            pointer(0xE0 + 2 * (op - 0x40), p['ornament'])
            if channel == 'C':
                put(p['orn_pos'], 0)
            else:
                alt[2] = alt[4]
        elif channel == 'B' and op >= 0x20:
            put(0xDF67, op - 0x20)
            continue
        elif op >= 0x10:
            mask = 0
            if op != 0x10:
                period(op - 0x10)
                mask = 0x10
            envelope(mask, True)
            pointer(0xA0 + take(), p['sample'])
        else:
            if op not in HANDLERS[channel]:
                raise ValueError(('reserved_effect_word', channel, op))
            low = (0xE0 + 2 * op + p['effect_anchor']) & 255
            address = p['effect_page'] * 256 + low
            handler = m[address] + 256 * m[(address & 0xFF00) | ((low + 1) & 255)]
            assert handler == HANDLERS[channel][op]
            sp -= 2
            put(sp + 1, handler >> 8)
            put(sp, handler & 255)
            hl = handler
            effects.append(op)
            if channel == 'C':
                put(0xE6EC, m[0xE2B9])
            continue
        bc = 0x1020
    else:
        raise ValueError('unterminated_pattern_row')

    # Применение параметров в обратном порядке команд, согласно физическому RET-стеку.
    for effect in reversed(effects):
        sp += 2
        if effect in (1, 2):
            delay = take()
            put(p['delay'], delay)
            if channel == 'C':
                put(p['reload'], delay)
            if effect == 1:
                hl = take_word()
                word(p['step'], hl)
                put(p['branch'], 0x1D)
                a = 0x1D
                if channel == 'C':
                    put(p['counter'], 0)
                    a, f = 0, 0x44
            else:
                take_word()
                word(p['step'], take_word())
                put(p['branch'], 0)
                target, previous = m[p['pending']], m[p['current']]
                put(p['target'], target)
                put(p['pending'], previous)
                hl = p['pending']
                bc &= 255
                a, f = (target if channel == 'C' else previous), 0x44
                if channel == 'C':
                    put(p['counter'], 0)
            if channel != 'C':
                alt[5] = alt[4]
        elif effect in (3, 4):
            a = take()
            put(p['sample_pos' if effect == 3 else 'orn_pos'], a)
            if channel != 'C':
                put(p['sample_gate' if effect == 3 else 'orn_gate'], 6)
                a = 6
        elif effect == 5:
            first, second = take(), take()
            put(p['on'], first)
            if channel == 'C':
                put(p['counter'], first)
            put(p['off'], second)
            a = second
            if channel != 'C':
                put(p['gate'], 6)
                a = 6
        elif effect == 8:
            put(0xDF74, take())
            hl = take_word()
            word(0xDF6E, hl)
            put(0xDF6B, 6)
            a = 6
        elif effect == 9:
            a = take()
            put(0xDF62, a)
    return dict(memory=m, writes=writes, commands=commands, effects=effects,
                main=[a, f, bc >> 8, bc & 255, de >> 8, de & 255, hl >> 8, hl & 255],
                alternate=alt, sp=sp + 2)
