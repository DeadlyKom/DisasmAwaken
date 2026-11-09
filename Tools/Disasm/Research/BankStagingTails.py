"""Границы реально копируемого LDIR хвоста за концом шести полос BANK."""

FORMAT = 'BANK_STRIP_STAGING_TAIL'
RANGES = {
    33: (0x1C92, 0x1CE3),
    34: (0x1CFE, 0x1D49),
    35: (0x1CB6, 0x1D07),
    36: (0x1B66, 0x1BD5),
    37: (0x1B4E, 0x1BB7),
    38: (0x1D16, 0x1D61),
}


def path_for(slot):
    return f'Source/Resources/{slot}_BANK{slot - 33}/StripStagingTail.bin'


def remaining_path(slot, begin, end):
    return f'Source/Resources/{slot}_BANK{slot - 33}/Unclassified{begin:04X}_{end:04X}.bin'


def split_gap(slot, gap_offset, gap_length):
    begin, end = RANGES[slot]
    limit = gap_offset + gap_length
    assert gap_offset == begin < end < limit
    return [(begin, end - begin, 'binary_resource', path_for(slot)),
            (end, limit - end, 'unclassified', remaining_path(slot, end, limit))]
