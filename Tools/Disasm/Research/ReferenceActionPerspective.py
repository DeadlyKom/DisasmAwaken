"""Числовая перспектива ACTION, дополненное частное и единицы нормализации не заменяются предпросмотром."""
from PreviewPerspectiveOracle import signed, flags16, absolute_context, rejected_axis_context
from CheckActionCloseBounds import arithmetic


def divide_context(magnitude, depth):
    assert depth > 0 and magnitude < 128 * depth
    if magnitude == 0 and depth >= 256:
        return dict(raw=0, af=(0, 0xAC), bias=0, quotient=0, normalization_shifts=16)
    bias, shifts = 0, 0
    if depth >= 256:
        first = 17 - magnitude.bit_length()
        for shifts in range(first, 17):
            upper = ((magnitude << shifts) + (1 << shifts) - 1) >> 16
            if upper >= depth >> 8 or shifts == 16:
                break
        if shifts > 8:
            bias = 256 - (1 << (16 - shifts))
    quotient, remainder = divmod(magnitude * 256 + bias, depth)
    raw = (~quotient) & 65535
    before = remainder + (depth if quotient & 1 else 0)
    flags = flags16(before, depth, True)
    final_flags = (flags & 0xC4) | (raw & 0x28) | ((raw >> 8) & 1)
    return dict(raw=raw, af=(raw & 255, final_flags), bias=bias, quotient=quotient, normalization_shifts=shifts)


def axis_context(value, base, exponent, depth, centre):
    magnitude, sign_af, sum_flags = absolute_context(value, base, exponent)
    if depth == 0 or magnitude >= 128 * depth:
        af = rejected_axis_context(magnitude, depth)
        # Ранний нормализованный отказ depth=256, magnitude=32768 успевает заменить младший C единицей.
        bc = (base & 0xFF00) | 1 if depth == 256 and magnitude == 32768 else base
        return dict(valid=False, af=af, alt_af=sign_af, bc=bc)
    division = divide_context(magnitude, depth)
    raw = division['raw']
    if sum_flags & 128:
        coordinate = (centre + raw) & 65535
        flags = (sign_af[1] & 0xC4) | (flags16(centre, raw) & 0x39)
    else:
        coordinate, flags = arithmetic(centre, raw, sign_af[1] & 1, False)
    return dict(valid=True, coordinate=coordinate, af=(sign_af[0], flags), alt_af=division['af'], bc=raw,
                quotient=division['quotient'], bias=division['bias'], shifts=division['normalization_shifts'])


def project(vertex, base, exponent, stack, initial_alt_af, initial_alt_bc):
    third, first, second = vertex
    depth_base, first_base, second_base = base
    term = (signed(third, 8) * (1 << (exponent - 1))) & 65535
    depth = (term + depth_base) & 65535
    if depth & 32768:
        reason = 'negative_depth'
        first_word, second_word = depth_base, 0x8000 | (depth_base & 255)
        af = (255 if third & 128 else 0, flags16(term, depth_base))
        alt_af, alt_bc = initial_alt_af, initial_alt_bc
        save_depth = False
    else:
        save_depth = True
        x = axis_context(first, first_base, exponent, depth, 48)
        if not x['valid']:
            reason = 'first_axis'
            first_word, second_word = depth, 0x8000 | (depth & 255)
            af, alt_af, alt_bc = x['af'], x['alt_af'], x['bc']
        else:
            first_word = x['coordinate']
            y = axis_context(second, second_base, exponent, depth, 128)
            af, alt_af, alt_bc = y['af'], y['alt_af'], y['bc']
            if not y['valid']:
                reason, second_word = 'second_axis', 0x8000 | (depth & 255)
            else:
                reason, second_word = 'accepted', y['coordinate']
    final_flags = (af[1] & 0xC4) | (flags16(9, (stack - 4) & 65535) & 0x39)
    return dict(reason=reason, first=first_word, second=second_word, af=(af[0], final_flags), alt_af=alt_af,
                alt_bc=alt_bc, alt_de=depth if reason == 'accepted' else second_word,
                alt_hl=(stack + 5) & 65535, depth=depth, save_depth=save_depth)
