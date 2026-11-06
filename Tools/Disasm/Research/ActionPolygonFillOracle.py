"""Конечные регистры линейной заливки из геометрии последних рёбер и переноса IX."""
from PreviewPolygonOracle import boundary, segment, PATTERNS
from PreviewEdgeRasterOracle import logical


def registers(vertices, mode):
    low = min(y for y, x in vertices)
    high = max(y for y, x in vertices)
    if low == high:
        return dict(degenerate=True, af=(high, 0x42 | (high & 0x28)), bc=1, de=high*257)
    left = boundary(vertices, high-1, -1)
    right = boundary(vertices, high-1, 1)

    def edge(direction):
        y0, x0, y1, x1 = segment(vertices, high-1, direction)
        height, delta = y1-y0, x1-x0
        step = -((-delta)//height) if delta else 1
        return x1, height//2, (0x2000+32*step)&65535

    left_end, left_error, left_step = edge(-1)
    right_end, right_error, right_step = edge(1)
    first, delta = PATTERNS[mode]
    pattern = first ^ (delta if (high-low)&1 else 0)
    # Расчёт переноса старшего байта линейного адреса до дробной коррекции левой границы.
    b = 0x80+low//8
    c = 0
    tail = high
    previous_edges = None
    for row in range(low, high):
        x = boundary(vertices, row, -1)
        right_x = boundary(vertices, row, 1)
        y0, x0, y1, x1 = segment(vertices, row, -1)
        edges = (segment(vertices, row, -1), segment(vertices, row, 1))
        # Обновление E при подготовке любой границы, затем при совмещении двух масок в одном байте.
        if edges != previous_edges:
            tail = y1
        if right_x//8 == x//8:
            tail = 255 ^ sum(128>>(column&7) for column in range(x, right_x))
        previous_edges = edges
        height, delta_x = y1-y0, x1-x0
        step = -((-delta_x)//height) if delta_x else 1
        increment = (0x2000+32*step)&65535
        # При обратном порядке крайних байтов строка пропускается с C левого края.
        c = ((row&7)<<5)|(max(x,right_x)//8)
        before = (((row&7)<<13)+x*32+mode*2)&65535
        if before+increment > 65535:
            b = (b+1)&255
    return dict(degenerate=False, af=(high, 0x42|(high&0x28)), bc=b*256+c, de=high*256+tail,
                ix=(((high&7)<<13)+left_end*32+mode*2)&65535,
                iy=(((high&7)<<13)+right_end*32+mode*2+16)&65535,
                alt_hl=right_error*256+left_error, alt_bc=left_step, alt_de=right_step,
                alt_af=(pattern, logical(pattern)))
