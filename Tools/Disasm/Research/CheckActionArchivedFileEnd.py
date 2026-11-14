"""Граница старого SP.C и физические хвосты исходного TRD и SCL."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from ProbeShipPreviewCallbacks import payload
from CheckIntro import ROOT
from PackedResourceCodec import decode


def compare_archived_sp(archive):
    with ZipFile(archive) as bundle:
        disk = bundle.read('awk5.trd')
    slot = 68
    header = disk[slot * 16:(slot + 1) * 16]
    assert header[:9] == b'SP      C'
    address, length = (int.from_bytes(header[i:i + 2], 'little') for i in (9, 11))
    disk_start = (16 * header[15] + header[14]) * 256
    archived = disk[disk_start:disk_start + header[13] * 256]
    current = payload(17)
    assert (address, length, len(archived)) == (0x6000, 0x984B, 0x9900)
    assert archived[length - 3:length] == bytes.fromhex('C3 1E F7')
    assert current[0x9863:0x9866] == bytes.fromhex('C3 35 F7')
    # Ветви адресуют те же места с поправкой #17. Хвост вызова меняет кадр IX.
    delta = 0x17
    assert int.from_bytes(archived[length - 2:length], 'little') + delta == 0xF735
    start, end = 0x97C6, 0x984F
    relocated = bytearray(archived[start - delta:end - delta])
    addresses = (0x97D8, 0x97DD, 0x97E4, 0x97EF, 0x97F7, 0x9806,
                 0x980B, 0x9810, 0x981C, 0x9823, 0x982A)
    for offset in addresses:
        index = offset - start
        old = int.from_bytes(relocated[index:index + 2], 'little')
        relocated[index:index + 2] = (old + delta).to_bytes(2, 'little')
    target = 0x97CC - start
    assert relocated[target:target + 2] == b'\x7E\xF0'
    relocated[target:target + 2] = b'\x75\xF0'
    assert relocated == current[start:end]
    assert archived[end - delta:length] == bytes.fromhex('11 61 EF 19 7E 23 66 6F 11 45 F8 D5 E9 CD 61 E5 C3 1E F7')
    assert current[end:0x9866] == bytes.fromhex('11 50 EF 19 7E 23 66 6F DD E5 11 5E F8 D5 E9 DD E1 CD 5C E5 C3 35 F7')
    assert archived[length:] == bytes(0xB5) and current[0x9866:] == bytes(0x79A)
    return dict(archive_sha256=sha256(archive.read_bytes()).hexdigest(), disk_member='awk5.trd', slot=slot,
                archived_origin=address, archived_logical_end_exclusive=address + length,
                archived_sector_end_exclusive=address + len(archived), archived_sector_suffix_bytes=0xB5,
                current_origin=0x6000, current_dispatch_end_exclusive=0xF866,
                current_logical_end_exclusive=0x10000, current_loaded_zero_tail_bytes=0x79A,
                compared_dispatch_prefix_bytes=end - start, relocated_operands=addresses,
                class18_target_old=0xF07E, class18_target_current=0xF075,
                historical_loop_target=0xF71E, current_loop_target=0xF735)


def compare_scl(archive):
    with ZipFile(archive) as bundle:
        scl = bundle.read('AWAK_SDC.SCL')
    assert scl[:8] == b'SINCLAIR' and int.from_bytes(scl[-4:], 'little') == sum(scl[:-4])
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    renamed = {3: (b'_awaken_B', b' AWAKEN B'), 25: (b'PANELN  C', b'PANEL   C'),
               28: (b'PANEL   C', b'PANELFF C')}
    assert scl[8] == 28
    results = []
    panels = {}
    position = 9 + 14 * scl[8]
    for index, slot in enumerate(range(3, 31)):
        header = scl[9 + 14 * index:23 + 14 * index]
        size = 256 * header[13]
        entry = disk[slot * 16:(slot + 1) * 16]
        disk_start = (16 * entry[15] + entry[14]) * 256
        physical = scl[position:position + size]
        assert header[9:] == entry[9:14] and physical == disk[disk_start:disk_start + size]
        assert (header[:9], entry[:9]) == renamed.get(slot, (header[:9], header[:9]))
        results.append(dict(scl_index=index, trd_slot=slot, scl_key=header[:9].decode('cp866'),
                            trd_key=entry[:9].decode('cp866'), allocated_bytes=size,
                            logical_bytes=int.from_bytes(entry[11:13], 'little'),
                            physical_sha256=sha256(physical).hexdigest()))
        if slot in (25, 28):
            packed = int.from_bytes(physical[4:6], 'little')
            raster = decode(physical[:packed], physical[packed:packed + 2])['data']
            assert len(raster) == 6912
            panels[slot] = dict(packed_bytes=packed, unpacked_bytes=len(raster),
                                unpacked_sha256=sha256(raster).hexdigest(), byte_at_daeb=raster[0x1AEB])
        position += size
    assert position == len(scl) - 4 and panels[25]['byte_at_daeb'] == 0x04
    return dict(archive_sha256=sha256(archive.read_bytes()).hexdigest(),
                scl_checksum_verified=True, files=results, panel_screens=panels)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    parser.add_argument('scl_archive', type=Path)
    args = parser.parse_args()
    reports = ROOT / 'Tools/Disasm/Reports'
    result = dict(passed=True, archived_dispatch=compare_archived_sp(args.source_archive),
                  scl_physical_identity=compare_scl(args.scl_archive),
                  original_disk_purpose_of_tail_proved=False, assembly_executed=False, native_execution=False)
    (reports / 'ActionArchivedFileEndVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Сверены граница архивного SP.C и полные сектора всех 28 файлов SCL.')


if __name__ == '__main__':
    main()
