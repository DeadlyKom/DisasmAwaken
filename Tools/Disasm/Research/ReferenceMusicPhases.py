"""Числовая модель распределённой подготовки B/C с настоящей семантикой декодеров."""
from ReferenceMusicPattern import decode


def dec_flags(old, carry):
    value = (old - 1) & 255
    return (value & 0xA8) | (0x40 if not value else 0) | (4 if old == 128 else 0) | (16 if not old & 15 else 0) | 2 | carry


def advance_bc(source, main, alternate, stack=0xBFFE):
    m = list(source)
    r, alt = list(main), list(alternate)
    writes = []
    old = m[0xE37D]
    carry = r[1] & 1

    def put(address, value):
        m[address] = value
        writes.append((address, value))

    def word(address, value):
        put(address, value & 255)
        put(address + 1, value >> 8)

    def parse(channel, hl, de, saved, return_address):
        nonlocal m
        put(stack - 1, return_address >> 8)
        put(stack - 2, return_address & 255)
        result = decode(m, channel, de=de, hl=hl, alternate=saved, stack=stack - 2)
        assert result['sp'] == stack
        m = result['memory']
        writes.extend(result['writes'])
        return result['main'], result['alternate']

    put(0xE37D, (old - 1) & 255)
    if old == 1:
        put(0xDE1F, 1)
        row = m[0xDC0F]
        put(0xDC0F, (row - 1) & 255)
        r[0], r[1], r[6], r[7] = 1, dec_flags(row, carry), 0xDC, 0x0F
        if row == 1:
            stream = m[0xE3C4] + 256 * m[0xE3C5]
            r, alt = parse('C', 0xDB0F, stream, alt, 0xE3CB)
            word(0xE3C4, r[4] * 256 + r[5])
            r[0] = m[0xE3D0]
            put(0xDC0F, r[0])
            old_b = r[2]
            r[2] = (old_b - 1) & 255
            r[1] = dec_flags(old_b, r[1] & 1)
            if old_b == 1:
                r[6:8] = [0, 0]
                word(0xE296, 0)
    elif old == 2:
        row = m[0xDC0E]
        put(0xDC0E, (row - 1) & 255)
        flags = dec_flags(row, carry)
        saved = [alt[0], alt[1], 0x18, r[3], 6, 0x18, 0x18, 0x0E]
        working = [0, flags] + alt[2:8]
        if row == 1:
            stream = m[0xE393] + 256 * m[0xE394]
            working, saved = parse('B', 0xDB00 | alt[7], stream, saved, 0xE39A)
            word(0xE393, working[4] * 256 + working[5])
            working[0] = m[0xE39F]
            put(0xDC0E, working[0])
        old_b = working[2]
        working[2] = (old_b - 1) & 255
        put(0xDEBC, 0x22 if old_b == 1 else 1)
        alt = [saved[0], saved[1]] + working[2:8]
        r = [saved[5], working[1]] + saved[2:8]
        put(0xDEEF, r[2])
        put(0xDEBF, r[6])
        put(0xDF00, r[5])
    else:
        r[0] = (old - 2) & 255
        r[1] = dec_flags((old - 1) & 255, carry)
    return dict(memory=m, writes=writes, main=r, alternate=alt, sp=stack + 2)


def advance_a(source, main, alternate, stack=0xBFFE):
    m = list(source)
    writes = []
    old = m[0xDE1E]
    flags = dec_flags(old, main[1] & 1)
    saved = [alternate[0], alternate[1], main[5], main[3], main[4], main[5], main[5], 0x1E]
    working = [main[0], flags] + list(alternate[2:8])
    position_changed = looped = False

    def put(address, value):
        m[address] = value
        writes.append((address, value))

    def word(address, value):
        put(address, value & 255)
        put((address + 1) & 65535, value >> 8)

    def read_word(address):
        return m[address] + 256 * m[(address + 1) & 65535]

    put(0xDE1E, (old - 1) & 255)
    if old == 1:
        stream = read_word(0xDF89)
        lookup_hl = (0xDB00 | working[7])
        if m[stream] == 0:
            position_changed = True
            put(0xDF67, 0)
            word(0xDFBD, stack)
            position_address = read_word(0xDF98)
            if m[position_address] == 255:
                position_address = read_word(0xDF9F)
                looped = True
            position = m[position_address]
            word(0xDF98, (position_address + 1) & 65535)
            # Расчёт фактического смещения, байт позиции прибавляется дважды, а не умножается на шесть.
            table = (read_word(0xDFA7) + 2 * position) & 65535
            module = read_word(0xDFAE)
            pointers = [(read_word((table + offset) & 65535) + module) & 65535 for offset in (0, 2, 4)]
            stream = pointers[0]
            word(0xE393, pointers[1])
            word(0xE3C4, pointers[2])
            lookup_hl = 0xDB00 | (pointers[2] & 255)
        put(stack - 1, 0xDF)
        put(stack - 2, 0xC4)
        result = decode(m, 'A', de=stream, hl=lookup_hl, alternate=saved, stack=stack - 2)
        assert result['sp'] == stack
        m = result['memory']
        writes.extend(result['writes'])
        working, saved = result['main'], result['alternate']
        word(0xDF89, working[4] * 256 + working[5])
        working[0] = m[0xDFC9]
        put(0xDE1E, working[0])
    old_b = working[2]
    working[2] = (old_b - 1) & 255
    put(0xDE2E, 0x22 if old_b == 1 else 1)
    alt = [saved[0], saved[1]] + working[2:8]
    r = [saved[5], working[1]] + saved[2:8]
    put(0xDE61, r[2])
    put(0xDE31, r[6])
    put(0xDE72, r[5])
    return dict(memory=m, writes=writes, main=r, alternate=alt, sp=stack,
                position_changed=position_changed, looped=looped)
