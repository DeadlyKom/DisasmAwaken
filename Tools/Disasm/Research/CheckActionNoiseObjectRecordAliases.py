"""Условные обращения шумового ROM IRQ к неизвестным хвостам FActionRecord."""
from hashlib import sha256
import json
from pathlib import Path

from CheckActionNoiseExit import COPY_SEED, R, NoiseIrqMemory, ROM48, ROM128, irq_noise_frame, put, run_to
from CheckActionNoiseLetterCase import LetterA, boot_noise, run_seeded_frame
from CheckIntro import ROOT
from ReferenceControlsPointRespawn import refresh


class ObjectTailMemory(NoiseIrqMemory):
    watch_objects = False

    def __init__(self):
        super().__init__()
        self.object_accesses = []

    def observe_tail(self, mode, address, value):
        super().observe_tail(mode, address, value)
        if (self.watch_objects and isinstance(address, int) and 0xA100 <= address < 0xA780
                and (address - 0xA100) % 64 >= 0x27 and self.registers[24] < 0x4000):
            self.object_accesses.append((mode, self.registers[24], address, value))


def check_rom(path):
    rom = Path(path).read_bytes()
    words = [int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little') for seed in range(256)]
    assert [seed for seed, word in enumerate(words) if word == 0xA72B] == [0x95]
    # Проверка зависимости найденных хвостовых псевдонимов от старшего разряда R.
    low_seed_tail_addresses = sorted({(iy + offset) & 65535 for iy in words[:128]
        for offset in (1, 7, 0x30, 0x40)
        if 0xA100 <= (iy + offset) & 65535 < 0xA780 and ((iy + offset - 0xA100) & 65535) % 64 >= 0x27})
    assert not low_seed_tail_addresses
    cpu = boot_noise(rom, memory_type=ObjectTailMemory)
    memory = cpu.memory
    assert all(memory[address] == 0 for address in (0xA72C, 0xA732, 0xA76B))
    cpu.set_tracer(LetterA(cpu, 2))
    memory.watch_objects = True
    iy, increment = run_seeded_frame(cpu, words, 0x95, 0x5C3A)
    assert iy == 0xA72B and increment is None and not memory.object_accesses
    # Второй кадр сохраняет естественный ход R после подготовленного первого копирования.
    run_to(cpu, COPY_SEED)
    second_seed = refresh(cpu.registers[R], 2)
    assert second_seed & 128
    put(memory, 0x5C78, b'\xFF\xFF')
    observed, _, _, increment = irq_noise_frame(cpu, iy)
    assert observed == second_seed
    memory.watch_objects = False
    expected = [('read', 0x0045, 0xA76B, 0), ('write', 0x0045, 0xA76B, 1)]
    if rom[0x3870:0x3874] == bytes.fromhex('fdcb0166'):
        expected.append(('read', 0x3870, 0xA72C, 0))
    expected.extend([('read', 0x02FC, 0xA732, 0), ('read', 0x02FF, 0xA72C, 0),
                     ('read', 0x030B, 0xA72C, 0), ('write', 0x030B, 0xA72C, 0x20)])
    assert memory.object_accesses == expected, memory.object_accesses
    assert increment == dict(address=0xA76B, old=0, new=1, bank0=False)
    assert [memory[address] for address in (0xA72C, 0xA732, 0xA76B)] == [0x20, 0, 1]
    return dict(rom=Path(path).name, rom_sha256=sha256(rom).hexdigest(), first_copy_seed=0x95,
                previous_frame_iy=iy, no_aliases_for_seed_bit7_clear=True,
                second_copy_seed=second_seed, second_frame_refresh_not_reassigned=True,
                accesses=[dict(mode=m, pc=pc, address=a, value=v, physical_bank=2)
                          for m, pc, a, v in expected], frame_increment=increment)


def main():
    profiles = [check_rom(path) for path in (ROM48, ROM128[1])]
    fields = [dict(address=0xA72C, instance='ActionObjectRecords.Record18', field='Unknown2C'),
              dict(address=0xA732, instance='ActionObjectRecords.Record18', field='Unknown32'),
              dict(address=0xA76B, instance='ActionObjectRecords.EndMarker', field='Unknown2B')]
    report = dict(passed=True, profiles=profiles, physical_fields=fields,
                  actual_rom_irq_and_viewport_copy_executed=True,
                  refresh_bit7_and_frames_wrap_prepared=True, key_A_prepared_at_second_irq=True,
                  source_record_tail_purpose_proved=False, native_refresh_bit7_reachability_proved=False,
                  action_initialization_trdos_substituted=True,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseObjectRecordAliasesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Обе ROM: подтверждены условные IRQ-псевдонимы Unknown2C, Unknown32 и Unknown2B маркера.')


if __name__ == '__main__':
    main()
