"""Числовые комбинации группы и точная перспектива ACTION, без исполнения инструкций."""
from PreviewVertexGroupOracle import combinations, byte_combinations, packed_negative, rotate
from ReferenceActionPerspective import project

WORD_TARGETS = {0: 0xD706, 1: 0xD73A, 3: 0xD747, 2: 0xD756, 5: 0xD77B, 4: 0xD788, 6: 0xD761, 7: 0xD76E}
BYTE_TARGETS = {5: 0xD77E, 4: 0xD78B, 6: 0xD764, 7: 0xD771}


def group(words, thirds, tag, base, exponent, offset, alternates):
    input_low = words[0] & 255
    words = combinations(*words, packed_negative)
    depths = byte_combinations(*thirds)
    if tag == 1:
        vertices = [(words[0], depths[0])]
    elif tag == 129:
        vertices = [(words[0], depths[0]), (packed_negative(words[0]), (-depths[0]) & 255)]
    else:
        vertices = [(words[i], depths[i]) for i in (0, 1, 3, 2, 6, 7, 5, 4) if tag & (1 << i)]
    stack = 0x8E00 + offset
    alt_af, alt_bc, alt_de, alt_hl = alternates
    points = []
    last_flags = 0
    for packed, third in vertices:
        vertex = (third, packed & 255, packed >> 8)
        out = project(vertex, base, exponent, stack, alt_af, alt_bc)
        points.append((stack, out))
        alt_af, alt_bc, alt_de, alt_hl = out['alt_af'], out['alt_bc'], out['alt_de'], out['alt_hl']
        last_flags = out['af'][1]
        stack += 5
    if tag not in (1, 129) and not tag & 16:
        last_flags = 0x44
    return dict(words=words, depths=depths, vertices=vertices, points=points, stack=stack,
        af=(stack & 255, (last_flags & 0xC4) | ((stack >> 8) & 0x28)),
        bc=(tag << 8) | rotate(input_low), de=vertices[-1][0] if tag in (1, 129) else words[4],
        ix=(((-depths[0]) & 255) if tag == 129 else depths[0]) * 256 + depths[2],
        iy=depths[1] * 256 + depths[3], alt_af=alt_af, alt_bc=alt_bc, alt_de=alt_de, alt_hl=alt_hl)
