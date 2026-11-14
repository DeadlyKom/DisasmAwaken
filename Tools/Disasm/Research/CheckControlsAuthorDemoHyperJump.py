"""Исполняет предшественник RunTemporaryModule в авторском AWAKEN_D.SCL."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckBasicIntroDiskRead import prepare_memory
from CheckControlsLegacySectorRead import SectorPorts, run_with_rom
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator
from CheckScreenUpdate import put
from PackedResourceCodec import decode
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import A, IFF, IXh, IXl, T


DATA_START = 0x33
MAIN = 0x24636
CONTROL0 = 0x29533
CONTROL = 0x2B033
OBJECTS = 0x2C633
RETURN = 0x3FFF


def unpack(blob, offset):
    assert blob[offset:offset + 2] == b'HR'
    size = int.from_bytes(blob[offset + 4:offset + 6], 'little')
    end = offset + size
    return decode(blob[offset:end], blob[end:end + 2])['data']


def sector_index(offset):
    # Первые 16 секторов занимает служебная дорожка при последовательной раскладке SCL.
    return (offset - DATA_START) // 256 + 16


def sector_word(offset):
    track, sector = divmod(sector_index(offset), 16)
    return bytes((sector, track))


def sector_range(offset, count):
    first = sector_index(offset)
    return [(index // 16, index % 16 + 1) for index in range(first, first + count)]


def current_variant():
    control = (ROOT / 'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    control0 = (ROOT / 'Tools/Disasm/Extracted/Active/22_CONTROL0.C.bin').read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert control[6:13] == bytes.fromhex('3E 16 01 FD 7F ED 79')
    assert control[0x1A:0x25] == bytes.fromhex('3E 11 ED 79 D9 21 00 C6 01 00 00')
    assert control[0x48:0x4B] == bytes.fromhex('CD 00 65')
    assert control[0x7C:0x7F] == bytes.fromhex('C3 00 60')
    assert control0[0x600:0x602] != b'HR'
    assert bytes.fromhex('2A 0F C0 11 A0 5D D5 ED 4B 11 C0 ED B0') not in disk
    return dict(control_sha256=sha256(control).hexdigest(), initial_packed_length=0,
                effect_source=0xC600, continuation=0x6000, exact_demo_transfer_signature_found=False)


class DemoPorts(SectorPorts):
    def __init__(self, scl, memory):
        super().__init__(bytes(0x1000) + scl[DATA_START:-4], retry=False)
        self.memory = memory
        self.pages = []
        self.ay = []

    def write_port(self, registers, port, value, offset):
        if port == 0x7FFD:
            self.memory.out7ffd(value)
            self.pages.append(value)
        elif port in (0xFFFD, 0xBFFD):
            self.ay.append((port, value))
        elif port & 255 != 0xFE:
            super().write_port(registers, port, value, offset)

    def read_port(self, registers, port):
        if registers[PC] >= 0x4000:
            return 255
        return super().read_port(registers, port)


def initialize(scl, main, control0, control, objects, basic, dos):
    memory = SliceableMemory(out7ffd=0x10)
    memory.roms = (basic, basic)
    memory.memory[0] = basic
    put(memory, 0x5C00, prepare_memory(basic)[0x5C00:0x5D25])
    put(memory, 0x5CC2, b'\xF1\xC9')
    memory[0x5D16] = 0xC7
    put(memory, 0x5CF4, sector_word(CONTROL0))
    put(memory, 0x5CF7, sector_word(MAIN))
    put(memory, 0x6000, main)
    ports = DemoPorts(scl, memory)
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A},
                    config={'fast_ldir': True, 'fast_djnz': True})
    cpu.set_tracer(ports)

    def set_rom(image):
        memory.memory[0] = image

    run_with_rom(cpu, basic, dos, set_rom, 0x42AC, step_limit=1_500_000)
    assert ports.attempts == sector_range(CONTROL0, 27) + sector_range(CONTROL, 22) + sector_range(OBJECTS, 52)
    assert bytes(memory.banks[3][:len(control0)]) == control0
    assert bytes(memory.banks[4][:len(control)]) == control
    assert bytes(memory.banks[6][:len(objects)]) == objects
    assert bytes(memory[0x721B:0x7226]) == bytes.fromhex('21 01 2C 06 16 11 07 2D 3E 34 C9')
    run_with_rom(cpu, basic, dos, set_rom, 0x9D49, step_limit=1_500_000)
    assert memory.o7ffd == 0x10 and cpu.registers[SP] == 0xBFFF
    return cpu, ports


def jump(cpu, ports, basic, dos, control, effect, objects, fuel, distance):
    memory, registers = cpu.memory, cpu.registers
    original_ix = registers[IXh] * 256 + registers[IXl]
    original_sp = registers[SP]
    registers[PC] = 0x71A9
    registers[SP] -= 2
    put(memory, registers[SP], RETURN.to_bytes(2, 'little'))
    put(memory, 0x9261, fuel)
    put(memory, 0x92F4, bytes((distance, 0)))
    sector_before, pages_before = len(ports.attempts), len(ports.pages)
    allowed = (fuel[1] if fuel[1] else fuel[0] // 2) >= distance
    charged = None
    irq = 0
    period, pulse = 70908, 36
    next_int = registers[T] + period
    dos_paged = False
    checkpoints = []
    for steps in range(9_000_000):
        pc = registers[PC]
        if pc == RETURN:
            break
        if pc == 0x71E0:
            charged = bytes(memory[0x9261:0x9263])
        if pc == 0x7219:
            assert memory.o7ffd == 0x14 and memory[0xC7B6] == memory[0x720D] == 0xC7
            wrapper = bytes(memory[0xC6D0:0xC82E])
            changed = [i for i, (a, b) in enumerate(zip(wrapper, control[0x6D0:0x82E])) if a != b]
            assert changed == [0xC7B6 - 0xC6D0], changed
        if pc == 0x5DA0:
            assert memory.o7ffd == 0x14
            assert bytes(memory[0x5DA0:0x5EFE]) == wrapper
            checkpoints.append(pc)
        if pc == 0x5DAE:
            assert bytes(memory[0x5E31:0x5E35]) == bytes.fromhex('01 2C 06 16')
            assert bytes(memory[0x5E49:0x5E4D]) == bytes.fromhex('07 2D 06 34')
            core = bytes(memory[0x6000:0x8000])
            checkpoints.append(pc)
        if pc == 0x5DC5:
            work = bytes(memory[0x8C00:0xC000])
            assert registers[SP] == original_sp - 4
        if pc == 0x6500:
            assert bytes(memory[0x6400:0x6400 + len(effect)]) == effect
            assert bytes(memory[0x5FFE:0x6000]) == b'\xF9\x5D'
            assert bytes(memory.banks[7][:0x3400]) == work
            assert bytes(memory.banks[4][0x2000:]) == core
            checkpoints.append(pc)
        if pc == 0x5DF9:
            assert registers[SP] == 0x6000 and memory.o7ffd == 0x16
            assert bytes(memory.banks[7][:0x3400]) == work
            assert bytes(memory.banks[4][0x2000:]) == core
            checkpoints.append(pc)
        if pc == 0x5E13:
            assert memory.o7ffd == 0x10 and bytes(memory[0x8C00:0xC000]) == work
            checkpoints.append(pc)
        if pc == 0x5E30:
            assert memory.o7ffd == 0x14 and bytes(memory[0x6000:0x8000]) == core
            checkpoints.append(pc)
        if pc == 0x5E48:
            assert bytes(memory.banks[4][:len(control)]) == control
            assert ports.attempts[sector_before:] == sector_range(CONTROL, 22)
            checkpoints.append(pc)
        if pc == 0x5E54:
            assert bytes(memory.banks[6][:len(objects)]) == objects
            checkpoints.append(pc)
        if pc == 0x5E5D:
            assert bytes(memory[pc:pc + 3]) == b'\xCD' + bytes(memory[0x9221:0x9223])
            assert bytes(memory[pc + 1:pc + 3]) == bytes.fromhex('EF 6D')
            checkpoints.append(pc)
        if dos_paged and pc >= 0x4000:
            memory.memory[0] = basic
            dos_paged = False
        elif not dos_paged and 0x3D00 <= pc < 0x3E00:
            memory.memory[0] = dos
            dos_paged = True
        cpu.run()
        while registers[T] >= next_int + pulse:
            next_int += period
        if registers[T] >= next_int and registers[IFF] and cpu.accept_interrupt(registers, memory, pc):
            irq += 1
    else:
        raise AssertionError(('граница возврата', hex(registers[PC]), hex(registers[SP])))
    assert registers[SP] == original_sp
    assert registers[IXh] * 256 + registers[IXl] == original_ix
    assert memory.o7ffd == 0x10
    reads = ports.attempts[sector_before:]
    remaining = bytes(memory[0x9261:0x9263])
    if allowed:
        assert reads == sector_range(CONTROL, 22) + sector_range(OBJECTS, 52)
        assert checkpoints == [0x5DA0, 0x5DAE, 0x6500, 0x5DF9, 0x5E13, 0x5E30, 0x5E48, 0x5E54, 0x5E5D]
        expected = bytes((0, fuel[1] - distance)) if fuel[1] else bytes((2 * (fuel[0] // 2 - distance), 0))
        assert charged == remaining == expected and irq > 0, (fuel, charged, expected, remaining, irq)
        assert ports.ay[-2:] == [(0xFFFD, 7), (0xBFFD, 0xDB)]
    else:
        assert not reads and not checkpoints and len(ports.pages) == pages_before
        assert remaining == fuel and irq == 0 and registers[A] < distance
    return dict(initial_fuel=list(fuel), distance=distance, allowed=allowed,
                fuel_after_charge=list(charged) if charged is not None else None,
                fuel_after_return=list(remaining),
                disk_reads=len(reads), control_sectors=reads[:22], object_sectors=reads[22:],
                hardware_interrupts_modeled=irq, checkpoints=checkpoints, return_pc=registers[PC],
                return_sp=registers[SP], return_bank_port=memory.o7ffd, simulator_steps=steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    archive_bytes = args.archive.read_bytes()
    assert sha256(archive_bytes).hexdigest() == '9f58746be8a339575234f0823d41d0e2481eb75910d9439a10aff90eef4b87a6'
    with ZipFile(args.archive) as archive:
        scl = archive.read('AWAKEN_D.SCL')
    assert scl[:9] == b'SINCLAIR\x03'
    assert sum(scl[:-4]) & 0xFFFFFFFF == int.from_bytes(scl[-4:], 'little')
    main_image, control0, control = (unpack(scl, offset) for offset in (MAIN, CONTROL0, CONTROL))
    objects = scl[OBJECTS:OBJECTS + 0x3400]
    effect = unpack(control, 0x1B)
    assert len(effect) == 2444 and control[0x0F:0x13] == bytes.fromhex('D0 C6 5E 01')
    assert control[0x19:0x1B] == bytes.fromhex('B6 C7')
    assert main_image[:16] == bytes.fromhex('AF D3 FE 21 10 60 11 00 42 D5 01 C3 02 ED B0 C9')
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 0x4000
    profiles = []
    for fuel, distance in ((b'\x64\0', 3), (b'\0\x64', 3), (b'\x02\0', 3)):
        cpu, ports = initialize(scl, main_image, control0, control, objects, basic, dos)
        profiles.append(jump(cpu, ports, basic, dos, control, effect, objects, fuel, distance))
    report = dict(passed=True, source='AWAKEN_D.SCL', archive_sha256=sha256(archive_bytes).hexdigest(),
                  dos_rom_sha256=sha256(dos).hexdigest(), bootstrap_sectors=101, caller_entry=0x71A9,
                  copy_source=0xC6D0, copy_target=0x5DA0, copy_bytes=0x15E, packed_effect_bytes=0x6B5,
                  unpacked_effect_bytes=len(effect), genuine_demo_loader_and_disk_routines=True,
                  demo_main_sha256=sha256(main_image).hexdigest(), demo_control_sha256=sha256(control).hexdigest(),
                  demo_effect_sha256=sha256(effect).hexdigest(), awaken_v02=current_variant(),
                  original_demo_bootstrap_fixture_origin=0x6000, fuel_and_distance_fixture=True,
                  native_execution=False, assembly_executed=False, current_game_caller_proved=False,
                  profiles=profiles)
    path = ROOT / 'Tools/Disasm/Reports/ControlsAuthorDemoHyperJumpVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print('Проверены три профиля архивного гиперпрыжка, 101 сектор начальной загрузки и 74 сектора каждого успешного перехода')


if __name__ == '__main__':
    main()
