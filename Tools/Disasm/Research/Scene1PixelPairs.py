"""Исследовательская геометрия двух чередующихся битовых плоскостей scene1po.s."""
WIDTH=368
HEIGHT=203
ROW_BYTES=46
LOGICAL_BYTES=18676
SLOT=30
PATH='Source/Resources/30_scene1po/PixelPairs.bin'
TAIL_PATH='Source/Resources/30_scene1po/SectorTail.bin'
FORMAT='SCENE1_INTERLEAVED_BITMAP_PLANES'


def unpack(data):
    assert len(data)==LOGICAL_BYTES==2*ROW_BYTES*HEIGHT and WIDTH==8*ROW_BYTES
    planes=[bytearray(WIDTH*HEIGHT),bytearray(WIDTH*HEIGHT)]
    for y in range(HEIGHT):
        for column in range(ROW_BYTES):
            for plane in range(2):
                value=data[y*2*ROW_BYTES+2*column+plane]
                for bit in range(8):planes[plane][y*WIDTH+8*column+bit]=(value>>(7-bit))&1
    return tuple(bytes(p) for p in planes)


def pack(planes):
    assert len(planes)==2 and all(len(p)==WIDTH*HEIGHT for p in planes)
    result=bytearray()
    for y in range(HEIGHT):
        for x in range(0,WIDTH,8):
            for plane in planes:
                value=0
                for bit in plane[y*WIDTH+x:y*WIDTH+x+8]:
                    assert bit in (0,1)
                    value=2*value+bit
                result.append(value)
    return bytes(result)
