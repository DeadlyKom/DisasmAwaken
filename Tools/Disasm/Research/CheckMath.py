"""Проверка исходных арифметических процедур на ограниченных наборах входов."""

from pathlib import Path
import itertools
import json
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, D, E, H, L


def execute(simulator, registers, pair):
    simulator.registers[:] = get_registers(registers, None, False)
    # Проверка выхода через установленный адрес возврата или JP (IX).
    for steps in range(2000):
        if simulator.registers[PC] == 0x3FFF:
            first, second = pair
            return 256*simulator.registers[first]+simulator.registers[second]
        simulator.run()
    raise ValueError("Арифметическая процедура не завершилась в установленной границе")


def main():
    memory = [0]*65536
    text = (ROOT / "Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    memory[0xC000:0xC000+len(text)] = text
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator = Simulator(memory)
    values = [0,1,2,127,128,255,256,257,32767,32768,65535]
    functions = {
        0xC3D5:("CompareEqual", lambda x,y:int(x==y)),
        0xC3DF:("MultiplyWithChecks", lambda x,y:min(x*y,65535)),
        0xC488:("AddSaturated", lambda x,y:min(x+y,65535)),
        0xC491:("SubtractSaturated", lambda x,y:max(x-y,0)),
        0xC49C:("CompareLess", lambda x,y:int(x<y)),
        0xC4A6:("CompareGreater", lambda x,y:int(x>y)),
        0xC4B1:("CompareNotGreater", lambda x,y:int(x<=y)),
        0xC4BC:("CompareNotLess", lambda x,y:int(x>=y)),
        0xC4C6:("AndWords", lambda x,y:x&y),
        0xC4CD:("OrWords", lambda x,y:x|y),
    }
    results = []
    for address, (name, formula) in functions.items():
        differences = []
        for left, right in itertools.product(values, repeat=2):
            actual = execute(simulator, {"PC":address, "SP":0xBFFE, "DE":left, "BC":right}, (D,E))
            expected = formula(left,right)
            if actual != expected:
                differences.append(dict(left=left,right=right,actual=actual,mathematical_expected=expected))
        if address != 0xC3DF and differences:
            raise ValueError("Неожиданное отличие арифметики " + name)
        results.append(dict(name=name,address=address,fixtures=len(values)**2,
                            formula_matches=not differences,differences=differences))
    # Проверка масштабированного умножения отдельного 3D-модуля.
    memory = [0]*65536
    data = (ROOT / "Tools/Disasm/Extracted/Active/19_3DPART.C.bin").read_bytes()
    memory[0xC000:0xC000+len(data)] = data
    simulator = Simulator(memory)
    coefficients = [-127,-64,-32,-16,-2,-1,0,1,2,16,32,64,127]
    operands = [-32768,-32767,-1000,-257,-256,-128,-1,0,1,127,128,255,256,257,1000,32767]
    failures = []
    for coefficient, operand in itertools.product(coefficients, operands):
        actual = execute(simulator, {"PC":0xD12C,"A":coefficient&255,"DE":operand&65535,"IX":0x3FFF}, (H,L))
        magnitude = abs(coefficient*operand)//128
        expected = (-magnitude if coefficient*operand<0 else magnitude)&65535
        if actual != expected:
            failures.append(dict(coefficient=coefficient,operand=operand,actual=actual,expected=expected))
    if failures:
        raise ValueError("Неожиданное отличие масштабированного умножения")
    results.append(dict(name="MultiplySignedScaled",address=0xD12C,
                        fixtures=len(coefficients)*len(operands),formula_matches=True,
                        formula="truncate_toward_zero(coefficient * operand / 128)",
                        coefficient_range="tested values within -127..127", differences=[]))
    report = dict(method="original_bytes_in_isolated_skoolkit", full_domain_proof=False,
                  game_code_modified=False, results=results)
    (ROOT / "Tools/Disasm/Reports/MathVerification.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
    for result in results:
        print(result["name"],result["fixtures"],"fixtures",len(result["differences"]),"differences")


if __name__ == "__main__":
    main()
