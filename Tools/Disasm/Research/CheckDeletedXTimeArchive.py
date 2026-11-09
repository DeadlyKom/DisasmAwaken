"""Проверка распаковщика из удалённой записи ZXTime и извлечение его результата."""
from hashlib import sha256
import json

from CheckUnpackResource import ROOT, Simulator, decode, get_registers, PC, SP


def main():
    folder = ROOT / 'Tools/Disasm/Extracted/Deleted'
    sectors = (folder / '00__XTime15.B.sectors.bin').read_bytes()
    logical = (folder / '00__XTime15.B.bin').read_bytes()
    assert logical == sectors[:327] and b'zxtime#0F' in logical
    assert logical[0x37:0x42] == bytes.fromhex('21 00 60 06 26 CD 86 5D CD 00 60')
    loader = 0x200
    stream = 0x303
    assert sectors[loader:loader + 5] == bytes.fromhex('F3 ED 73 FD 60')
    assert sectors[stream - 3:stream] == bytes.fromhex('C3 00 60')
    packed_size = int.from_bytes(sectors[stream + 4:stream + 6], 'little')
    packed = sectors[stream:stream + packed_size]
    expected = decode(packed, sectors[stream + packed_size:stream + packed_size + 2])['data']
    assert packed_size == 9350 and len(expected) == 40960

    memory = [0] * 65536
    loaded = sectors[loader:loader + 38 * 256]
    memory[0x6000:0x6000 + len(loaded)] = loaded
    memory[0x5FFE:0x6000] = [0x43, 0x5D]
    simulator = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFE},
                          config={'fast_ldir': False, 'fast_djnz': False})
    initial = get_registers({'PC': 0x6000, 'SP': 0x5FFE, 'AF': 0x5AC5}, None, False)
    simulator.registers[:] = initial
    entered_copy = False
    for steps in range(500000):
        simulator.run()
        pc = simulator.registers[PC]
        entered_copy |= pc == 0x5B00
        if pc == 0x6000:
            break
    else:
        raise AssertionError(('ZXTime не достиг перехода к распакованному коду', hex(pc)))
    assert entered_copy and simulator.registers[SP] == 0x5FFE
    assert bytes(memory[0x6000:]) == expected
    assert expected[0x6C00:].startswith(b'ProTracker 3.6 compilation of')

    target = folder / '00__XTime15.B.unpacked.bin'
    if target.exists():
        assert target.read_bytes() == expected
    else:
        target.write_bytes(expected)
    report = dict(passed=True, deleted_slot=0, logical_bytes=len(logical), archive_file_offset=stream,
                  archive_disk_offset=0x1000 + stream, packed_bytes=packed_size, decoded_bytes=len(expected),
                  decoded_sha256=sha256(expected).hexdigest(), decoded_path=target.relative_to(ROOT).as_posix(),
                  loader_entry=0x6000, copied_code_entry=0x5B00, restored_stack=0x5FFE,
                  expanded_entry=0x6000, executed_instructions=steps + 1,
                  independent_decoder_and_original_instructions_agree=True,
                  sectors_preloaded_for_model=True, expanded_application_executed=False,
                  catalog_and_disk_unchanged=True, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/DeletedXTimeArchiveVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
