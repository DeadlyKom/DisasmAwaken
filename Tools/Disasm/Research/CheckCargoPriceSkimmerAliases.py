"""Условные чтения Price хвостом ComputeWeightedLoad при байтовом индексе скимера.

Документация: ../../../Docs/CargoField.md
Документация: ../../../Docs/WeightedLoad.md
"""
from collections import defaultdict
from hashlib import sha256
import json

from CheckCargoPriceTradeAccess import (
    ROOT, PriceMemory, PRICE_ADDRESSES, Simulator, get_registers,
    PC, SP, make_context, put, probe,
)
from CheckMatrixKey import add_flags
from skoolkit.simutils import A, F, C, R


def main():
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    sources = {}
    # Проверка физических байтов фикстуры и полного исходного хвоста расчёта.
    for slot in (4, 5, 7):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        source = (ROOT / (entry['path'] + '.sectors.bin')).read_bytes()
        assert source == disk[entry['offset']:entry['offset'] + entry['allocated_length']]
        sources[slot] = source
    code = sources[5][0x8EB:0x900]
    assert code == bytes.fromhex('3a4a983c280d3d5f0707835f1600212998197e81c9')
    _, _, banks = make_context()
    banks[6][:len(sources[5])] = sources[5]
    probe()
    aliases = defaultdict(list)
    cases = price_reads = 0
    for option in range(256):
        # Расчёт адреса по байтовому вращению, старшие биты кода возвращаются в младшие.
        offset = ((((option << 2) | (option >> 6)) & 255) + option) & 255
        address = None if option == 255 else 0x9829 + offset
        if address in PRICE_ADDRESSES:
            aliases[(address - 0x9853) // 2].append(option)
        for pattern in range(3):
            memory = PriceMemory(banks=[bank.copy() for bank in banks], out7ffd=0x16)
            for row, target in enumerate(PRICE_ADDRESSES):
                memory[target] = (0, 255, (73 * row + 19) & 255)[pattern]
            memory[0x984A] = option
            put(memory, 0x7FFE, [255, 63])
            for total in (0, 1, 127, 128, 255):
                # Оригинальный хвост принимает сумму в C, остальные таблицы и циклы здесь не исполняются.
                cpu = Simulator(memory)
                cpu.registers[:] = get_registers(dict(PC=0xC8EB, SP=0x7FFE,
                    HL=0x1357, DE=0x2468, BC=0xAB00 + total, AF=0x5A5D,
                    R=0xF9, IX=0x5678, IY=0x5C3A), None, False)
                saved = list(cpu.registers)
                memory.registers = cpu.registers
                value = 0 if address is None else memory[address]
                memory.price_reads.clear()
                memory.price_writes.clear()
                memory.price_recording = True
                for _ in range(20):
                    if cpu.registers[PC] == 0x3FFF:
                        break
                    cpu.run()
                else:
                    raise AssertionError(('Хвост расчёта не вернулся', option))
                memory.price_recording = False
                registers = cpu.registers
                # Проверка адреса чтения, байтовой суммы, флагов и сохранённых регистров.
                assert registers[A] == (value + total) & 255
                assert registers[F] == add_flags(value, total)
                assert registers[2:4] == saved[2:4] and registers[C] == total
                expected_pairs = saved[4:8] if address is None else [0, offset, address >> 8, address & 255]
                assert registers[4:8] == expected_pairs
                assert registers[8:12] == saved[8:12] and registers[14] == saved[14]
                assert registers[16:24] == saved[16:24] and registers[26:] == saved[26:]
                assert registers[SP] == 0x8000
                increments = 5 if address is None else 15
                assert registers[R] == (saved[R] & 128) | ((saved[R] + increments) & 127)
                expected_reads = [(0xC8FD, address, value)] if address in PRICE_ADDRESSES else []
                assert memory.price_reads == expected_reads and memory.price_writes == []
                price_reads += len(expected_reads)
                cases += 1
    assert cases == 3840 and len(aliases) == 12
    assert not any(option in (0, 1, 2, 3, 255) for values in aliases.values() for option in values)
    result = dict(passed=True, cases=cases, original_disk_sha256=manifest['sha256'],
        original_physical_files_checked=[4, 5, 7], original_tail_start=0xC8EB,
        original_tail_end_exclusive=0xC900, original_tail_sha256=sha256(code).hexdigest(),
        all_256_skimmer_bytes_tested=True, input_sums=[0, 1, 127, 128, 255],
        price_patterns=['zero', 'FF', '73*row+19 modulo 256'],
        price_aliases=[dict(row=row, address=PRICE_ADDRESSES[row], skimmer_codes=values)
                       for row, values in sorted(aliases.items())],
        conditional_price_rows=12, observed_price_reads=price_reads, price_writes=0,
        all_30_CPU_read_write_probes_passed=True, result_flags_registers_and_exact_R_checked=True,
        valid_four_record_indices_and_FF_do_not_read_prices=True,
        full_weighted_load_or_trade_script_executed=False,
        out_of_range_codes_native_origin_proved=False, all_RAM_and_cycle_bus_sequence_compared=False,
        IRQ_executed=False, assembly_executed=False, native_execution=False)
    target = ROOT / 'Tools/Disasm/Reports/CargoPriceSkimmerAliasesVerification.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, cases=cases, price_rows=len(aliases), price_reads=price_reads)))


if __name__ == '__main__':
    main()
