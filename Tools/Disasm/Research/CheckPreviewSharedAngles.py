"""Архивные Eye_a/Eye_g и начальные углы рабочего прохода D3D."""
from hashlib import sha256
import json
import re
import struct
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckPreviewQueueBuild import ROOT, Simulator, Memory, payload, get_registers, PC


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        _, source, _ = read_entry(archive.read('awk6.trd'), b'DATA3D  a')
        _, renderer, _ = read_entry(archive.read('awk6.trd'), b'CLPXR1  a')
    definitions = {}
    for row in source.split(b'\r'):
        match = re.fullmatch(rb'(Eye_[abg]|Eye[abg])\x06.\x05f\x06\x82#([0-9A-F]{4})', row)
        if match:
            definitions[match[1].decode()] = int(match[2], 16)
    assert definitions == dict(Eye_a=0xC200, Eye_b=0xC201, Eye_g=0xC202,
                               Eyea=0xC21E, Eyeb=0xC21F, Eyeg=0xC220)
    rows = renderer.split(b'\r')
    start = rows.index(b'Ren3d')
    copy = [row for row in rows[start + 1:start + 7] if row]
    assert copy == [b'\x06\x8c\x05 \x06\x83\x03\x8c,(Eye_a)',
                    b'\x06\x8c\x05 \x06\x83(Eyea),\x05\x8c',
                    b'\x06\x8c\x05 \x06\x83\x03~,(Eye_g)',
                    b'\x06\x8c\x05 \x06\x83(Eyeg),\x05~']
    raw = payload(6)
    assert raw[0x2C28:0x2C34] == bytes.fromhex('2a00c2221ec23a02c23220c2')
    memory = Memory([0] * 65536)
    memory[0xC000:0xC000 + len(raw)] = raw
    saved = memory.copy()
    cpu = Simulator(memory)
    initial = get_registers(dict(SP=0x7FFE, HL=0x1357, DE=0x2468, BC=0x369C,
                                 AF=0x5A5D, IX=0x2468, IY=0x5C3A), None, False)
    counts = dict(empty=0, object=0)
    for populated in (False, True):
        for slot in (0, 2):
            for value in range(256):
                memory.recording = False
                memory[:] = saved
                seeds = [3, 5, 7]
                seeds[slot] = value
                memory[0xC200:0xC203] = seeds
                for row in range(3):
                    for column in range(3):
                        memory[0xC20D + 2 * (3 * column + row)] = 127 if row == column else 0
                if populated:
                    memory[0xCDC0:0xCDC0 + 10] = struct.pack('<3H4B', 0, 0, 1500, 0, 11, 22, 33)
                terminal = 0xCE00 if populated else 0xCDC0
                memory[terminal:terminal + 2] = [128, 128]
                memory[0x7FFE:0x8000] = [255, 63]
                cpu.registers[:] = initial
                cpu.registers[PC] = 0xEC28
                memory.writes = []
                memory.recording = True
                for _ in range(4):
                    cpu.run()
                assert cpu.registers[PC] == 0xEC34
                assert memory[0xC21E:0xC221] == seeds
                assert memory.writes == list(zip(range(0xC21E, 0xC221), seeds))
                for _ in range(30000):
                    if cpu.registers[PC] == 0xEEEE:
                        break
                    cpu.run()
                else:
                    raise AssertionError(('Не завершён обход', populated, slot, value))
                assert memory[0xC21E:0xC221] == ([11, 22, 33] if populated else seeds)
                assert memory[0xC200:0xC203] == seeds
                counts['object' if populated else 'empty'] += 1
    report = dict(passed=True, archive_sha256=digest, source='awk6.trd:DATA3D.a,CLPXR1.a',
                  authored_definitions=definitions, matched_copy_bytes=12,
                  original_copy_hex=raw[0x2C28:0x2C34].hex(), cases=sum(counts.values()), profiles=counts,
                  each_first_and_third_seed_byte_exhausted=True, exact_initial_three_byte_writes=True,
                  object_angles_replace_initial_angles=True, empty_list_preserves_initial_angles=True,
                  seed_storage_unchanged=True, rendering_pass_executed=False,
                  global_camera_behavior_proved=False, irq_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/PreviewSharedAnglesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены начальные углы D3D:', report['cases'], 'сценария')


if __name__ == '__main__':
    main()
