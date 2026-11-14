"""Проверка шести изменяемых операндов рамки и полных регистров настройки режима."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from CheckPreviewCoordinateMultiply import Memory
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, SP

WORDS = (0xC095, 0xC0F2, 0xC0F8, 0xC0FF, 0xC13E, 0xC144)
NORMAL = (0xC1C0, 0xC1C0, 0xC1ED, 0xC1C0, 0xC1ED, 0xC1C0)
FILLED = (0xC1CF, 0xC1C0, 0xC1CF, 0xC1CF, 0xC1CF, 0xC1CF)
ALL_FILLED = (0xC1CF,) * len(WORDS)


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = Memory([0]*65536)
    memory[0x6000:] = source
    memory[0x7FFE:0x8000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    counts = {}; m1_by_entry = {start:set() for start in (0xCCAA,0xCCAF,0xCCD4)}
    assert bytes(memory[0xCCAA:0xCCAF]) == bytes.fromhex('11 cf c1 18 03')
    for start in (0xCCAA, 0xCCAF, 0xCCD4):
        for value in range(256):
            for flags in range(256):
                # Создание произвольных прежних значений подтверждает полную перезапись всех шести слов.
                for address in WORDS:
                    memory[address:address+2] = [0x34, 0x12]
                memory[0x99B4] = value
                memory[0xC0CA:0xC0CC] = [0x78, 0x56]
                simulator.registers[:] = initial
                simulator.registers[A], simulator.registers[F] = value if start == 0xCCD4 else value ^ 0xA5, flags
                r=simulator.registers;r[14]=value^flags;r[15]=flags;r[26]=flags>>7;r[27]=value%3;context=r.copy()
                memory.writes=[];memory.recording=True;simulator.run(start=start, stop=0x3FFF);memory.recording=False
                expected_m1=15 if start==0xCCD4 else (19 if value&1 else 18)+int(start==0xCCAA)
                assert r[15]==refresh(context[15],expected_m1) and all(r[i]==context[i] for i in (14,26,27))
                m1_by_entry[start].add(expected_m1)
                if start == 0xCCD4:
                    expected_a, expected_f, expected_de, expected_words = value, flags, 0xC1ED, NORMAL
                else:
                    expected_a = (value >> 1) | ((flags & 1) << 7)
                    expected_f = (flags & 0xC4) | (expected_a & 0x28) | (value & 1)
                    expected_de = 0xC1ED if value & 1 else 0xC1CF
                    expected_words = NORMAL if value & 1 else ALL_FILLED if start == 0xCCAA else FILLED
                # Проверка порядка всех двенадцати присваиваний, собственных записей стека и других ячеек нет.
                addresses=(0xC0FF,0xC144,0xC095,0xC0F2,0xC13E,0xC0F8) if expected_words==NORMAL else (0xC0F2,0xC13E,0xC0F8,0xC0FF,0xC144,0xC095)
                values=dict(zip(WORDS,expected_words))
                assert memory.writes==[(p+i,(values[p]>>(8*i))&255) for p in addresses for i in (0,1)],(hex(start),value,flags,memory.writes)
                actual_words = tuple(memory[p]+256*memory[p+1] for p in WORDS)
                if actual_words != expected_words or (simulator.registers[A], simulator.registers[F],
                        simulator.registers[D]*256+simulator.registers[E], simulator.registers[SP]) != (
                        expected_a, expected_f, expected_de, 0x8000):
                    raise ValueError("Не совпала настройка полосовой рамки")
                if memory[0x99B4] != value or memory[0xC0CA:0xC0CC] != [0x78, 0x56]:
                    raise ValueError("Настройщик изменил режим заливки либо уже выбранный BandPattern")
                for reg in (*range(2, 4), *range(6, 12), *range(16, 24)):
                    if simulator.registers[reg] != initial[reg]:
                        raise ValueError("Изменён сохраняемый регистр настройщика рамки")
                counts[f"{start:04X}"] = counts.get(f"{start:04X}", 0)+1
    report = dict(method="original_band_mode_patch_against_six_word_contract", passed=True,
                  cases=sum(counts.values()), by_entry=counts, source_sha256=hashlib.sha256(source).hexdigest(),
                  mutated_word_addresses=[f"{p:04X}" for p in WORDS],
                  full_m1_by_entry={f"{k:04X}":sorted(v) for k,v in m1_by_entry.items()},
                  exact_refresh_and_all_12_cpu_writes=True,i_im_iff_preserved=True,both_iff_values_without_irq=True,
                  irq_executed=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/BandModeVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
