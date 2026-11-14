"""Условное чтение четырёх Unknown-слов предложения кнопкой Контракт.

Документация: ../../../Docs/MissionOffer.md
Документация: ../../../Docs/ContractMap.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckRowHighlight import ROOT, Simulator, make_context
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, SP, PC, R


class Memory(list):
    recording = False

    def __getitem__(self, key):
        if self.recording:
            indices = (key,) if isinstance(key, int) else range(*key.indices(65536))
            self.offer_reads.extend(index for index in indices if 0x98B4 <= index < 0x98BC)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if self.recording:
            assert isinstance(key, int)
            self.writes.append((key, value))
        super().__setitem__(key, value)


def main():
    # Проверка физического происхождения всех локальных инструкций до общего хвоста.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entry = next(row for row in manifest['entries'] if row['slot'] == 4)
    source = (ROOT/(entry['path']+'.bin')).read_bytes()
    assert source == disk[entry['offset']:entry['offset']+entry['length']]
    _, _, banks = make_context()
    base = [0]*65536
    base[0x4000:0x8000], base[0x8000:0xC000], base[0xC000:] = banks[5], banks[2], banks[0]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    rows = [row for region in flow if region['name'] == 'Station'
            for row in region['instructions'] if 0x7CC6 <= row['address'] < 0x7CF8]
    assert rows[0]['address'] == 0x7CC6 and rows[-1]['address'] == 0x7CF6
    for row in rows:
        raw = bytes.fromhex(row['hex'])
        assert row['slot'] == 4
        assert source[row['offset']:row['offset']+len(raw)] == raw
        assert bytes(base[row['address']:row['address']+len(raw)]) == raw
    assert len(rows) == 28
    m = Memory(base)
    cpu = Simulator(m)
    # Положительный контроль чтения байта, слова и записи в наблюдаемой области через CPU.
    m[0x3000:0x3009] = bytes.fromhex('3AB4982AB69832B898')
    cpu.registers[:] = get_registers(dict(PC=0x3000, SP=0x7FFE), None, False)
    m.offer_reads, m.writes, m.recording = [], [], True
    for _ in range(3):
        cpu.run()
    m.recording = False
    assert m.offer_reads == [0x98B4, 0x98B6, 0x98B7] and m.writes == [(0x98B8, base[0x98B4])]
    counts, m1_counts = Counter(), set()
    profiles = []
    # Проверка всех ненулевых ROM-байтов, положительные выбирают следующие ключи, отрицательные первый.
    for rom in range(1, 256):
        for pattern in range(8):
            profiles.append((rom, bytes((pattern*29+i*37+11)&255 for i in range(8)), 'rom_patterns'))
    # Проверка чувствительности к каждому из восьми байтов при всех 256 его значениях.
    for index in range(8):
        for value in range(256):
            opaque = bytearray((i*37+11)&255 for i in range(8))
            opaque[index] = value
            profiles.append((1, bytes(opaque), 'individual_bytes'))
    for rom, opaque, category in profiles:
        m.recording = False
        m[:] = base
        m[1] = rom
        m[0x98B0:0x98B4] = bytes.fromhex('394B0600')
        m[0x98B4:0x98BC] = opaque
        m[0x98BF] = 0xA7
        m[0x7CCC:0x7CCE] = bytes.fromhex('A399')
        m[0x7FFE:0x8000] = bytes.fromhex('FF3F')
        # Повторный локальный вызов сохраняет записанный курсор и все данные первого вызова.
        for invocation in (1, 2):
            initial = get_registers(dict(PC=0x7CC6, SP=0x7FFE, HL=0x1357, DE=0x247A,
                BC=0x36C9, AF=0x5A5D, IX=0x2468, IY=0x5C3A,
                **{'^HL':0x369C, '^DE':0x47AD, '^BC':0x58BE, '^AF':0x69CF}), None, False)
            cpu.registers[:] = initial
            before = m.copy()
            m.offer_reads, m.writes, m.recording = [], [], True
            steps, m1 = 0, 0
            while cpu.registers[PC] != 0x7D14:
                pc = cpu.registers[PC]
                assert 0x7CC6 <= pc < 0x7CF8 and steps < 40
                m1 += 2 if m[pc] == 0xED else 1
                cpu.run()
                steps += 1
            m.recording = False
            r = cpu.registers
            cursor = 0x99A3 if rom & 128 else 0x99A3+invocation
            address = 0x98B0 if rom & 128 else 0x98B0+4*invocation
            key = before[address:address+4]
            expected = before.copy()
            expected[0x98BF] = 1
            expected[0x7CCC:0x7CCE] = [cursor&255, cursor>>8]
            assert m == expected
            assert m.writes == [(0x98BF, 1), (0x7CCC, cursor&255), (0x7CCD, cursor>>8)]
            assert m.offer_reads == ([] if rom & 128 else list(range(address, address+4)))
            assert r[D]*256+r[E] == key[0]+256*key[1] and r[H]*256+r[L] == key[2]+256*key[3]
            assert (r[A], r[F]) == (key[2], 0x48 if rom & 128 else 0x08)
            assert r[R] == (initial[R]&128)|((initial[R]+m1)&127)
            assert all(r[index] == initial[index] for index in (B,C,8,9,10,11,SP,*range(16,24)))
            assert m[0x7FFE:0x8000] == [255,63]
            m1_counts.add((bool(rom&128), steps, m1))
            counts['local_invocations'] += 1
            counts['first_offer_key' if rom&128 else 'opaque_key_'+str(invocation)] += 1
            counts[category] += 1
    assert m1_counts == {(False, 27, 28), (True, 28, 29)}
    result = dict(passed=True, method='two_original_local_invocations_with_observed_opaque_reads',
        original_disk_sha256=manifest['sha256'], physical_instruction_count=len(rows),
        counts=dict(counts), instruction_profiles=[dict(negative_rom=x, instructions=y, m1=z)
            for x,y,z in sorted(m1_counts)], all_nonzero_rom_bytes=True,
        all_values_of_each_opaque_byte=True, every_local_write_checked=True,
        full_ram_compared=True, exact_key_registers_flags_and_r_checked=True,
        all_four_words_conditionally_read=True, positive_probe_passed=True,
        cursor_preserved_between_local_invocations=True, stop_before_shared_center=True,
        stable_local_af_rom_selects_opaque_words=False, opaque_word_writers_proved=False,
        original_game_data_purpose_proved=False, full_map_redraw_executed=False,
        irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/MissionOfferIndirectKeysVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, counts=dict(counts), instruction_profiles=result['instruction_profiles']), indent=2))


if __name__ == '__main__':
    main()
