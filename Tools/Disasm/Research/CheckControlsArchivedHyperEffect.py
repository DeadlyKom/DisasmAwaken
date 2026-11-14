"""Сверяет авторский архив с CONTROL из Awakenv02 и исполняет архивный EFF отдельно."""
import argparse
import json
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

from CheckControlsTemporaryModule import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from PackedResourceCodec import decode


def digest(data):
    return sha256(data).hexdigest()


def read_entry(disk, name):
    for slot in range(128):
        entry = disk[slot * 16:(slot + 1) * 16]
        if entry[0] == 0:
            break
        if entry[:9] == name:
            address = int.from_bytes(entry[9:11], 'little')
            length = int.from_bytes(entry[11:13], 'little')
            start = (entry[15] * 16 + entry[14]) * 256
            return address, disk[start:start + length], disk[start + length:start + length + 2]
    raise ValueError(name)


def compare_control(archive_control, control):
    assert archive_control[0x7A:0x7C] == bytes.fromhex('ED B0')
    assert control[0x7C:0x7F] == bytes.fromhex('C3 00 60')
    substitutions = {
        0x04: ('30', '33'),
        0x23: ('35 05', '00 00'),
        0x43: ('0A AC', '23 AB'),
        0x6F: ('A5 CD', '70 C8'),
        0x86: ('4A', '4D'),
        0x8C: ('0A AC', '23 AB'),
        0x97: ('7E E3', '87 DD'),
        0xB0: ('CF', 'D2'),
        0xB7: ('D3', 'D6'),
        0xCF: ('CF', 'D2'),
        0xD7: ('CF', 'D2'),
        0xDD: ('CF', 'D2'),
        0xE6: ('CF', 'D2'),
        0xEF: ('D3', 'D6'),
        0x101: ('D3', 'D6'),
        0x120: ('CF', 'D2'),
        0x127: ('D3', 'D6'),
        0x12C: ('5E', '61'),
    }
    expected = bytearray(archive_control[:0x138])
    for offset, (old, new) in substitutions.items():
        replacement = bytes.fromhex(new)
        assert expected[offset:offset + len(replacement)] == bytes.fromhex(old)
        expected[offset:offset + len(replacement)] = replacement
    expected[0x7C:0x7C] = bytes.fromhex('C3 00 60')
    assert expected == control[:0x13B]
    return {f'{offset:04X}': dict(archive=old, target=new)
            for offset, (old, new) in substitutions.items()}


def check_authored_source(archive_disk):
    _, equs, _ = read_entry(archive_disk, b'EQUS    a')
    _, caller, _ = read_entry(archive_disk, b'SETCONTRa')
    _, loader, _ = read_entry(archive_disk, b'SETHJRETa')
    _, space, _ = read_entry(archive_disk, b'SPACE   a')
    _, labels, _ = read_entry(archive_disk, b'LABELS  a')
    assert b'ADHDP\x06\x87\x05f\x06\x82#5DA0\r' in equs
    assert b'MESAG\x06\x83_HIPER\r' in caller
    assert bytes.fromhex('068c05200683038c') + b',$M18\r' in caller
    assert bytes.fromhex('068c05200683038b') + b',ADHDP\r' in caller
    assert bytes.fromhex('068c052d20058b0d068c05200683038a') + b',$M20\r' in caller
    assert b',$M20\r' + bytes.fromhex('068c05500d068c05240d') in caller
    assert b'$M18\r\x06\x8c\x05\x9bADHDP\r$M19\r' in loader
    assert b'$M20\x06\x88\x05f\x06\x82$-$M19\r' in loader
    assert b',JL1\r' in loader and b',JL2\r' in loader and b' #6500\r' in loader
    assert b'JL1:\r\x06\x8c\x05m"EFF.cod"\rJL2:' in space
    assert b'JL1\x06\x8c\x04f50688\r' in labels
    assert b'JL2\x06\x8c\x04f1333\r' in labels
    assert b'NEXTL2\x06\x89\x04f57363\r' in labels
    assert b'\rNDATA\r\x06\x8c\x05h\x06\x83#0122\r' in loader
    assert b'\rRETSTT\r' in loader
    assert b',NDATA\r' in loader and b',TIME\r' in loader


def compare_reset_context(archive_control, control):
    # Архивная машинная копия NDATA в TIME начинается с EXX и переносит 512 байтов.
    assert archive_control[0x20F:0x21C] == bytes.fromhex('D9 21 4B E1 11 BD 9B 01 00 02 ED B0 D9')
    old_template = archive_control[0x138:0x1BA]
    target_template = control[0x13B:0x1BD]
    assert old_template[:12] == target_template[:12]
    assert old_template[12:21] == bytes.fromhex('01 01 FF FF 00 40 9C 00 00')
    assert target_template[12:21] == bytes.fromhex('00 06 FF 00 00 D0 07 00 32')
    assert old_template[21:] == target_template[21:]
    return dict(archive_template_offset=0x138, archive_template_address=0xE14B,
                target_template_offset=0x13B, target_template_bytes=len(target_template),
                identical_prefix_bytes=12, changed_header_offsets=[12, 21],
                exact_suffix_offsets=[0x150, 0x1BD], exact_suffix_bytes=len(target_template[21:]),
                exact_suffix_sha256=digest(target_template[21:]),
                archive_copy_target=0x9BBD, archive_machine_copy_length=0x200,
                archive_source_copy_length=0x200, target_runtime_reader_proved=False)


def execute_effect(raw, return_address):
    banks = [bytearray(0x4000) for _ in range(8)]
    saved_core = bytes((i * 37 + 11) & 255 for i in range(0x2000))
    banks[1][0x2000:] = saved_core
    memory = RecordedBanks(banks=banks, out7ffd=0x11)
    put(memory, 0x6400, raw)
    put(memory, 0x5FFE, return_address.to_bytes(2, 'little'))
    sim = Simulator(memory, config={'fast_ldir': True, 'fast_djnz': True})
    sim.registers[:] = get_registers({'PC': 0x6500, 'SP': 0x5FFE}, None, False)
    trace = PortTrace(sim)
    sim.set_tracer(trace)
    frames = 0
    erased = False
    for steps in range(25000000):
        pc = sim.registers[PC]
        if pc == 0x6562:
            assert trace.writes[-1] == (0x7FFD, 0x11)
            assert bytes(banks[1][0x2000:]) == saved_core
        if pc == 0x6568:
            assert bytes(banks[1][0x2000:]) == bytes(0x2000)
            erased = True
        if pc == 0x6586:
            frames += 1
        if pc == return_address:
            break
        sim.run()
    else:
        raise AssertionError(('граница модели EFF', hex(sim.registers[PC]), frames))
    assert erased and frames == 300 and sim.registers[SP] == 0x6000
    assert bytes(memory[0x6593:0x6595]) == b'\xFE\x5F'
    restored_area = bytes(memory.banks[1][0x2000:])
    assert restored_area != saved_core
    return dict(frames=frames, simulator_steps=steps, return_pc=return_address,
                stack_after_return=0x6000, bank1_core_area_erased_before_frame_loop=True,
                bank1_core_area_sha256_after_return=digest(restored_area),
                bytes_equal_to_prepared_core=sum(a == b for a, b in zip(restored_area, saved_core)),
                paging_values=sorted({value for port, value in trace.writes if port == 0x7FFD}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    assert digest(args.archive.read_bytes()) == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
        sample = archive.read('awk5.trd')
    check_authored_source(disk)
    start, old_control, _ = read_entry(disk, b'CONTROL C')
    base, old_sp, _ = read_entry(sample, b'SP      C')
    assert start == 0xE013 and base == 0x6000
    assert old_sp[0x12C2:0x12CF] == bytes.fromhex('21 93 E1 11 A0 5D D5 01 38 01 ED B0 C9')
    assert old_sp[0xE193 - base:0xE193 - base + 0x138] != old_control[:0x138]
    target_disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    _, control, _ = read_entry(target_disk, b'CONTROL C')
    substitutions = compare_control(old_control, control)
    context = compare_reset_context(old_control, control)
    _, effect, tail = read_entry(disk, b'EFF     c')
    _, control0, _ = read_entry(disk, b'CONTROL0C')
    assert len(effect) == 0x535 and effect == control0[0x600:0xB35]
    assert effect not in target_disk and effect[:24] not in target_disk
    assert bytes.fromhex('11 A0 5D') not in target_disk
    raw = decode(effect, tail)['data']
    assert len(raw) == 0x79F and raw[0x100:0x104] == bytes.fromhex('F3 97 D3 FE')
    assert old_control[0x48:0x4B] == bytes.fromhex('CD 00 65')
    result = execute_effect(raw, 0x5DA0 + 0x4B)
    report = dict(passed=True, target_sha256=digest(target_disk), archive_sha256=digest(args.archive.read_bytes()),
                  awk1_sha256=digest(disk), awk5_sha256=digest(sample),
                  archive_control_sha256=digest(old_control), target_control_sha256=digest(control),
                  archive_caller_source='awk1.trd:SETCONTR.a',
                  archive_loader_source='awk1.trd:SETHJRET.a', archive_relocation_address=0x5DA0,
                  archive_control_load_address=start, archive_control_prefix_bytes=0x138,
                  target_control_prefix_bytes=0x13B, inserted_target_jump_offset=0x7C,
                  substitutions=substitutions, packed_effect_sha256=digest(effect),
                  unpacked_effect_sha256=digest(raw), packed_effect_bytes=len(effect),
                  unpacked_effect_bytes=len(raw), effect_offset_in_control0=0x600,
                  reset_context=context,
                  effect_execution=result, target_caller_proved=False,
                  historical_full_chain_executed=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ControlsArchivedHyperEffectVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
