"""Полная проверка табличных квадратов и разности квадратов на исходном Z80."""

from pathlib import Path
import collections
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP, R, I, IM, IFF
from ReferenceControlsPointRespawn import refresh


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 7)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert hashlib.sha256(disk).hexdigest() == manifest['sha256']
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    assert source[0x265D:0x2666] == bytes.fromhex('e5 26e9 6f 5e 24 56 e1 c9')
    memory = [0] * 65536
    memory[0xC000:0xC000 + len(source)] = source
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    refresh_costs = collections.Counter()
    initial_R_codes = {0xE65D:set(),0xE554:set()}
    witnesses = []

    def run(entry, value, first, carry):
        simulator.registers[:] = get_registers(
            {"PC": entry, "SP": 0xBFFE, "A": value, "F": 0xFE | carry,
             "DE": first * 256 + 0xAB, "HL": 0x1357, "BC": 0x2468,
             "IX": 0x789A, "IY": 0x5C3A}, None, False)
        simulator.registers[16:24] = [3, 17, 31, 43, 59, 71, 89, 101]
        initial_r = (value+first+carry)&255
        simulator.registers[R] = initial_r
        simulator.registers[I] = initial_r
        simulator.registers[IM] = first%3
        simulator.registers[IFF] = carry
        preserved_special = tuple(simulator.registers[i] for i in (I,IM,IFF))
        initial_R_codes[entry].add(initial_r)
        root = math.isqrt((first*first-value*value-carry)&65535)
        cost = 8 if entry == 0xE65D else 179-root.bit_count()
        witness = (value in (0,1,127,128,255)) if entry == 0xE65D else (first in (0,1,128,255) and value in (0,1,128,255))
        m1 = 0
        minimum_sp = simulator.registers[SP]
        for _ in range(250):
            if simulator.registers[PC] == 0x3FFF:
                assert simulator.registers[R] == refresh(initial_r,cost),(entry,first,value,carry,cost)
                assert tuple(simulator.registers[i] for i in (I,IM,IFF)) == preserved_special
                refresh_costs[entry,cost] += 1
                if witness:
                    assert m1 == cost
                    assert minimum_sp == (0xBFFC if entry == 0xE65D else 0xBFF2)
                    witnesses.append(dict(entry=entry,first=first,second=value,Carry=carry,
                        initial_R=initial_r,final_R=simulator.registers[R],observed_M1=m1,
                        input_SP=0xBFFE,minimum_SP=minimum_sp,final_SP=simulator.registers[SP]))
                return
            if witness:
                pc = simulator.registers[PC]
                opcode = memory[pc]
                assert opcode not in (0xDD,0xFD)
                assert memory[pc:pc+2] not in ([0xED,0x4F],[0xED,0x5F])
                m1 += 2 if opcode in (0xCB,0xED) else 1
            simulator.run()
            if witness:
                minimum_sp = min(minimum_sp,simulator.registers[SP])
                assert simulator.registers[R] == refresh(initial_r,m1)
        raise ValueError("Математическая процедура карты не завершилась")

    # Проверка всех 256 физических слов таблицы и сохранения обоих состояний Carry.
    for value in range(256):
        expected = value * value
        if source[0x2900 + value] + 256 * source[0x2A00 + value] != expected:
            raise ValueError("Таблица не содержит точные квадраты 0..255")
        for carry in (0, 1):
            run(0xE65D, value, 0xDB, carry)
            if (pair(D, E) != expected or pair(H, L) != 0x1357 or pair(B, C) != 0x2468
                    or simulator.registers[A] != value or simulator.registers[F] != 0xA8 | carry
                    or simulator.registers[SP] != 0xC000):
                raise ValueError("Неверный контракт LookupSquare")
    # Проверка полного диапазона двух байтовых аргументов и обоих входных заёмов.
    cases = 0
    for first in range(256):
        for second in range(256):
            for carry in (0, 1):
                run(0xE554, second, first, carry)
                target = (first * first - second * second - carry) & 0xFFFF
                if (simulator.registers[A] != math.isqrt(target) or simulator.registers[F] != 0x45
                        or pair(H, L) != 0x1357 or pair(B, C) != 0x2468
                        or pair(D, E) != first * 256 + 0xAB
                        or memory[0xDFB6] + 256 * memory[0xDFB7] != target
                        or simulator.registers[SP] != 0xC000
                        or simulator.registers[8:12] != [0x78, 0x9A, 0x5C, 0x3A]
                        or simulator.registers[16:24] != [3, 17, 31, 43, 59, 71, 89, 101]):
                    raise ValueError("Неверный контракт корня разности квадратов")
                cases += 1
    assert all(codes == set(range(256)) for codes in initial_R_codes.values())
    report = {"method": "original_z80_bytes_without_assembly", "square_table_words": 256,
              "square_lookup_cases": 512, "sqrt_difference_cases": cases,
              "full_byte_arguments_and_carry_domain": True, "flags_checked": True,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "map_rendering_verified": False, "assembly_executed": False,
              "refresh_verification": dict(cases=cases+512,lookup_exact_M1=8,
                  sqrt_M1='179-popcount(floor(sqrt((D*D-A*A-Carry) AND FFFF)))',
                  initial_R_codes_by_entry={format(e,'04X'):sorted(v) for e,v in initial_R_codes.items()},
                  cost_profiles=[dict(entry=e,M1=m1,cases=n) for (e,m1),n in sorted(refresh_costs.items())],
                  witnesses=witnesses,witness_count=len(witnesses),I_IM_IFF_preserved=True,
                  original_disk_sha256=manifest['sha256'],independent_R_argument_product_proved=False,
                  every_instruction_R_checked_only_in_witnesses=True,IRQ_executed=False)}
    report_path = ROOT / "Tools/Disasm/Reports/MapMathVerification.json"
    old = json.loads(report_path.read_bytes())
    def preserved(before,after):
        if isinstance(before,dict):
            assert isinstance(after,dict)
            for key,value in before.items():preserved(value,after[key])
        elif isinstance(before,list):
            assert isinstance(after,list) and len(before)==len(after)
            for a,b in zip(before,after):preserved(a,b)
        else:assert before==after
    preserved(old,report)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=True,sqrt_cases=cases,lookup_cases=512,witnesses=len(witnesses),costs=sorted({m1 for e,m1 in refresh_costs if e==0xE554})),ensure_ascii=False))


if __name__ == "__main__":
    main()
