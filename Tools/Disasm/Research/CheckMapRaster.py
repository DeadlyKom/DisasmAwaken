"""Проверка переходов строк Spectrum и нелокального выхода на исходных байтах карты."""

from pathlib import Path
import collections
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP, R, I, IM, IFF
from ReferenceControlsPointRespawn import refresh


class ObservedMemory(list):
    recording = False

    def __setitem__(self,index,value):
        if self.recording:
            assert isinstance(index,int)
            self.writes.append((index,value))
        super().__setitem__(index,value)


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 7)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert hashlib.sha256(disk).hexdigest() == manifest['sha256']
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    # Проверка двух прямолинейных сбросов, каждый состоит из восьми инструкций без префиксов.
    reset_bytes = {0xE666: bytes.fromhex('d9 210000 54 06ff d9 3e01 32b9df c9'),
                   0xE674: bytes.fromhex('d9 210000 54 06ff d9 af 32b9df c9')}
    for address,raw in reset_bytes.items():
        assert source[address-0xC000:address-0xC000+len(raw)] == raw
    memory = ObservedMemory([0] * 65536)
    memory[0xC000:0xC000 + len(source)] = source
    simulator = Simulator(memory)

    def word(address, value):
        memory[address:address + 2] = [value & 255, value >> 8]

    def row(base, y, x=0):
        return base | ((y & 7) << 8) | ((y & 0x38) << 2) | ((y & 0xC0) << 5) | x

    def pair(high, low):
        return 256 * simulator.registers[high] + simulator.registers[low]

    row_refresh_counts = collections.Counter()
    row_initial_R_codes = set()
    row_refresh_cases = 0

    def run(entry, pointer, other, upper, lower):
        nonlocal row_refresh_cases
        word(0xDFBA, upper)
        word(0xDFBC, lower)
        word(0xDFB4, 0xBFFA)
        word(0xBFF0, 0x3FFE)
        word(0xBFFA, 0x5AA5)
        word(0xBFFC, 0x3FFF)
        simulator.registers[:] = get_registers(
            {"PC": entry, "SP": 0xBFF0, "HL": pointer, "DE": 0x7700 | other,
             "BC": 0x1357, "AF": 0xDBA5, "IX": 0x789A, "IY": 0x5C3A,
             "^HL": 0x2468, "^DE": 0x369C, "^BC": 0x47AD, "^AF": 0x58BE}, None, False)
        initial_r = row_refresh_cases & 255
        simulator.registers[R] = initial_r
        simulator.registers[I] = initial_r
        simulator.registers[IM] = row_refresh_cases % 3
        simulator.registers[IFF] = row_refresh_cases & 1
        special_initial = tuple(simulator.registers[i] for i in (I,IM,IFF))
        row_initial_R_codes.add(initial_r)
        preserved = simulator.registers[8:12] + simulator.registers[16:24]
        high,low = pointer >> 8,pointer & 255
        # Расчёт стоимости по адресным разрядам и границе, независимо от PC исполненного пути.
        if entry == 0xE57E:
            expected_abort = pointer & 0xFFE0 == upper
            expected_m1 = 18 if expected_abort or high & 7 else 25 if low < 0x20 else 28
            pushed_pointer = pointer
        else:
            assert entry == 0xE5AC
            next_high = (high+1)&255
            next_low = low
            extra = 0
            if not next_high & 7:
                next_low = (low+0x20)&255
                extra = 7
                if low < 0xE0:
                    next_high = (next_high-8)&255
                    extra += 3
            pushed_pointer = next_high*256+next_low
            expected_abort = pushed_pointer & 0xFFE0 == lower
            expected_m1 = 17+extra+5*expected_abort
        m1 = 0
        memory.writes = []
        memory.recording = True
        for _ in range(64):
            if simulator.registers[PC] in (0x3FFE, 0x3FFF):
                break
            opcode = memory[simulator.registers[PC]]
            assert opcode not in (0xDD,0xFD)
            assert memory[simulator.registers[PC]:simulator.registers[PC]+2] not in ([0xED,0x4F],[0xED,0x5F])
            m1 += 2 if opcode in (0xCB,0xED) else 1
            simulator.run()
            assert simulator.registers[R] == refresh(initial_r,m1)
        else:
            raise ValueError("Растровый переход не завершился")
        memory.recording = False
        assert sorted(memory.writes) == [(0xBFEE,pushed_pointer&255),(0xBFEF,pushed_pointer>>8)]
        assert m1 == expected_m1,(entry,pointer,upper,lower,m1,expected_m1)
        assert simulator.registers[PC] == (0x3FFF if expected_abort else 0x3FFE)
        assert tuple(simulator.registers[i] for i in (I,IM,IFF)) == special_initial
        row_refresh_counts[entry,expected_abort,m1] += 1
        row_refresh_cases += 1
        if pair(B, C) != 0x1357 or preserved != simulator.registers[8:12] + simulator.registers[16:24]:
            raise ValueError("Изменились сохраняемые регистры растрового перехода")

    normal_cases = 0
    for base in (0x4000, 0x6000, 0x8000, 0xA000):
        for x in (0, 1, 15, 31):
            for other_x in (0, 31):
                for entry, delta, ys in ((0xE57E, -1, range(1, 192)), (0xE5AC, 1, range(191))):
                    for y in ys:
                        # Проверка всех внутренних строк, переходов третей и переноса обеих колонок.
                        upper, lower = row(base, 0), row(base, 192)
                        run(entry, row(base, y, x), row(base, y, other_x) & 255, upper, lower)
                        boundary = upper if delta < 0 else lower
                        if (pair(H, L) != row(base, y + delta, x)
                                or simulator.registers[E] != row(base, y + delta, other_x) & 255
                                or simulator.registers[D] != boundary >> 8
                                or simulator.registers[PC] != 0x3FFE or simulator.registers[SP] != 0xBFF2):
                            raise ValueError("Неверно перенесены адреса растровых колонок")
                        normal_cases += 1
    exits = 0
    for base in (0x4000, 0x6000, 0x8000, 0xA000):
        for x in (0, 1, 15, 31):
            for y in (0, 1, 7, 8, 63, 64, 127, 128, 191):
                for entry in (0xE57E, 0xE5AC):
                    # Проверка пропуска внутреннего возврата и восстановления независимого внешнего стека.
                    upper = row(base, y) if entry == 0xE57E else row(base, 0)
                    lower = row(base, y + 1) if entry == 0xE5AC else row(base, 192)
                    run(entry, row(base, y, x), row(base, y, 31 - x) & 255, upper, lower)
                    expected_y = y if entry == 0xE57E else y + 1
                    if (pair(H, L) != row(base, expected_y, x) or simulator.registers[PC] != 0x3FFF
                            or simulator.registers[SP] != 0xBFFE
                            or simulator.registers[A] != 0x5A or simulator.registers[F] != 0xA5):
                        raise ValueError("Неверно завершён внешний растровый вызов")
                    exits += 1
    resets = 0
    reset_initial_R_codes = set()
    for entry, direction in ((0xE666, 1), (0xE674, 0)):
        for flags in range(256):
            for alternate in (0, 0x1357, 0xFFFF):
                word(0xBFF0, 0x3FFE)
                simulator.registers[:] = get_registers(
                    {"PC": entry, "SP": 0xBFF0, "HL": 0x1357, "DE": 0x2468,
                     "BC": 0x9ABC, "AF": 0xDB00 | flags, "^HL": alternate,
                     "^DE": 0x67CD, "^BC": 0x89EF, "^AF": 0x5AA5,
                     "IX": 0x789A, "IY": 0x5C3A}, None, False)
                initial_r = flags ^ (alternate & 255)
                simulator.registers[R] = initial_r
                simulator.registers[I] = flags
                simulator.registers[IM] = flags % 3
                simulator.registers[IFF] = flags & 1
                reset_initial_R_codes.add(initial_r)
                special_initial = tuple(simulator.registers[i] for i in (I,IM,IFF))
                m1 = 0
                memory.writes = []
                memory.recording = True
                # Проверка полного входного F, частичного сброса альтернативного набора и байта направления.
                for _ in range(12):
                    if simulator.registers[PC] == 0x3FFE:
                        break
                    opcode = memory[simulator.registers[PC]]
                    assert opcode not in (0xCB,0xED,0xDD,0xFD)
                    simulator.run()
                    m1 += 1
                    assert simulator.registers[R] == refresh(initial_r,m1)
                else:
                    raise ValueError("Сброс растрового состояния не вернулся")
                memory.recording = False
                assert memory.writes == [(0xDFB9,direction)]
                assert m1 == 8
                assert tuple(simulator.registers[i] for i in (I,IM,IFF)) == special_initial
                expected_f = flags if direction else 0x44
                if (pair(H, L), pair(D, E), pair(B, C), simulator.registers[A], simulator.registers[F]) != (
                        0x1357, 0x2468, 0x9ABC, direction, expected_f):
                    raise ValueError("Неверен основной контракт сброса растрового состояния")
                if (simulator.registers[16:24] != [0x5A, 0xA5, 0xFF, 0xEF, 0, 0xCD, 0, 0]
                        or simulator.registers[8:12] != [0x78, 0x9A, 0x5C, 0x3A]
                        or memory[0xDFB9] != direction or simulator.registers[SP] != 0xBFF2):
                    raise ValueError("Неверен альтернативный контракт сброса растрового состояния")
                resets += 1
    assert reset_initial_R_codes == set(range(256))
    assert row_initial_R_codes == set(range(256))
    assert row_refresh_cases == normal_cases+exits
    report = {"method": "original_z80_bytes_without_assembly", "normal_row_cases": normal_cases,
              "nonlocal_exit_cases": exits, "reset_cases": resets,
              "source_sha256": hashlib.sha256(source).hexdigest(), "passed": True,
              "whole_raster_algorithm_verified": False, "assembly_executed": False,
              "reset_refresh_verification": dict(cases=resets, exact_M1=8,
                  initial_R_codes=sorted(reset_initial_R_codes), every_instruction_R_checked=True,
                  I_IM_IFF_preserved=True, only_direction_byte_written=True, interrupt_injection=False,
                  original_disk_sha256=manifest['sha256'], physical_reset_code_bytes=27,
                  independent_A_F_R_product_proved=False),
              "row_refresh_verification": dict(cases=row_refresh_cases, every_instruction_R_checked=True,
                  exact_M1_from_input_addresses=True, I_IM_IFF_preserved=True,
                  only_two_PUSH_HL_bytes_written=True, initial_R_codes=sorted(row_initial_R_codes),
                  profiles=[dict(entry=a,nonlocal_exit=abort,M1=m1,cases=count)
                            for (a,abort,m1),count in sorted(row_refresh_counts.items())],
                  independent_initial_R_input_product_proved=False, interrupt_injection=False)}
    report_path = ROOT / "Tools/Disasm/Reports/MapRasterVerification.json"
    old = json.loads(report_path.read_bytes())
    for key,value in old.items():
        if key == 'reset_refresh_verification':
            assert all(report[key][k] == v for k,v in value.items())
        else:
            assert report[key] == value,key
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("reset_refresh_verification","row_refresh_verification")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
