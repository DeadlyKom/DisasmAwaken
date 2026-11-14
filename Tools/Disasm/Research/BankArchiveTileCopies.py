"""Точные части третьего внекаталожного слоя в пяти файлах BANK."""

from BankStagingTails import remaining_path
from CheckIntro import ROOT


FORMAT = 'BANK_ARCHIVE_TILE_LAYER_COPY'
RANGES = {
    33: (0x1CE3, 0x1DF7, 0x93F5B),
    34: (0x1D49, 0x1E12, 0x93FA6),
    35: (0x1D07, 0x1E12, 0x93F64),
    37: (0x1BB7, 0x1E12, 0x93E14),
    38: (0x1D61, 0x1E12, 0x93FBE),
}


def path_for(slot):
    return f'Source/Resources/{slot}_BANK{slot - 33}/ArchiveTileLayerCopy.bin'


def split_gap(slot, gap_offset, gap_length):
    begin, end, _ = RANGES[slot]
    limit = gap_offset + gap_length
    assert gap_offset == begin < end <= limit
    result = [(begin, end - begin, 'binary_resource', path_for(slot))]
    if end < limit:
        result.append((end, limit - end, 'unclassified', remaining_path(slot, end, limit)))
    return result


def verify_original(sources):
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    total = 0
    for slot, (begin, end, source) in RANGES.items():
        assert 0x9376F <= source < source + end - begin <= 0x9406F
        assert sources[slot][begin:end] == disk[source:source + end - begin]
        total += end - begin
    assert total == 1524
    return total
