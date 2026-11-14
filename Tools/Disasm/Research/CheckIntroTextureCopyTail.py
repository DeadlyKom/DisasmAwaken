"""Сравнение двух прогонов вступления с разным содержимым 41 байта хвоста."""
import json

from CheckIntroStationTransition import (
    IntroInput, IntroMemory, ROOT, Simulator, get_registers, original_memory,
)


SOURCE = 0x8F6B
RELOCATED = 0x746B
TEXTURE = 0xE3AB
LENGTH = 41


def execute(flat, rom, frames, tail):
    banks = [bytearray(0x4000) for _ in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    banks[2][:] = bytes(flat[0x8000:0xC000])
    banks[2][SOURCE - 0x8000:SOURCE - 0x8000 + LENGTH] = tail
    memory = IntroMemory(banks=banks, out7ffd=16)
    memory.roms = (list(rom), list(rom))
    memory.out7ffd(16)
    memory[0x5C00] = memory[0x5C04] = 255
    sim = Simulator(memory)
    trace = IntroInput(sim, frames)
    sim.set_tracer(trace)
    sim.registers[:] = get_registers({'PC': 0x6500, 'SP': 0x5FFF, 'IY': 0x5C3A}, None, False)
    sim.registers[27] = 1
    memory.registers = sim.registers

    # Прерывания выполняются по ROM, граница прогона находится перед первым вызовом TR-DOS.
    sim.run(0x6500, 0x5D3B, interrupts=True)
    sim.run(0x5D3B, 0x3D13, interrupts=True)
    memory.registers = None

    # Сверяем обе копии и проверяем перезапись временной копии до её чтения.
    assert bytes(memory[RELOCATED:RELOCATED + LENGTH]) == tail
    assert bytes(memory.scratch_copied[address] for address in range(TEXTURE, TEXTURE + LENGTH)) == tail
    assert set(range(TEXTURE, TEXTURE + LENGTH)) <= memory.scratch_overwritten[0x6A1B, 0xFF]
    assert not memory.scratch_pending and not memory.scratch_reads
    assert trace.polls == min(300, frames + 1)
    return memory, sim.registers, trace.writes


def main():
    flat = original_memory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    original = bytes(flat[SOURCE:SOURCE + LENGTH])
    # Каждая позиция получает свою метку, отличную от исходного байта.
    changed = bytes(range(0x20, 0x20 + LENGTH))
    assert all(before != after for before, after in zip(original, changed))
    profiles = []
    for frames in (0, 1, 2, 300):
        reference, reference_registers, reference_ports = execute(flat, rom, frames, original)
        candidate, candidate_registers, candidate_ports = execute(flat, rom, frames, changed)
        assert reference_registers == candidate_registers
        assert reference_ports == candidate_ports
        assert reference.o7ffd == candidate.o7ffd
        assert reference.accesses == candidate.accesses
        differences = [
            (bank, offset)
            for bank, (before, after) in enumerate(zip(reference.banks, candidate.banks))
            for offset, (left, right) in enumerate(zip(before, after))
            if left != right
        ]
        # Проверяем все восемь банков, включая сохранённую текстуру и оба экрана.
        assert differences == [(5, RELOCATED - 0x4000 + offset) for offset in range(LENGTH)], differences
        profiles.append(dict(frames=frames, equal_port_writes=len(reference_ports),
                             compared_ram_bytes=8 * 0x4000, ram_differences=len(differences)))

    report = dict(passed=True, source=SOURCE, relocated=RELOCATED, texture=TEXTURE,
                  texture_bank=1, overwrite_pc=0x6A1B, stop_pc=0x3D13,
                  length=LENGTH, original=original.hex(), replacement=changed.hex(),
                  profiles=profiles, disk_modified=False, assembly_executed=False)
    result = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/IntroTextureCopyTailVerification.json').write_text(result, encoding='utf-8')
    print(result, end='')


if __name__ == '__main__':
    main()
