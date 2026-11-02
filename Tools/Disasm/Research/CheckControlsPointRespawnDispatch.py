"""CB00, выбор CE16/CE5D и шага по всем байтовым индексам без подмены инструкций."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    base = base_memory()
    cases = 0
    zero_steps = []
    for control in range(256):
        memory = list(base)
        # Создание различимой страницы коэффициентов, её математический смысл здесь не предполагается.
        memory[0x9900:0x9A00] = [(i*73+31)&255 for i in range(256)]
        memory[0x9B95:0x9B98] = [0,0,control]
        memory[0xBFFE:0xC000] = [255,63]
        simulator = Simulator(memory)
        simulator.registers[:] = get_registers({'SP':0xBFFE,'PC':0xCB00},None,False)
        target = 0xCC78 if control else 0x3FFF
        for _ in range(80):
            if simulator.registers[PC] == target:
                break
            simulator.run()
        else:
            raise AssertionError(('пролог',control))
        if control:
            index = (-control)&255
            negative = bool(index&128)
            magnitude = (-index)&255 if negative else index
            step = ((magnitude<<2)+(2+(magnitude>>7) if negative else 0))&255
            selected = 0xCE5D if negative else 0xCE16
            assert memory[0xCE1E] == memory[0xCE65] == step
            assert memory[0xCD31:0xCD33] == memory[0xCDFC:0xCDFE] == [selected&255,selected>>8]
            first = memory[0x9900+index]
            second = memory[0x9900+((index+64)&255)]
            assert memory[0xCCD2] == first and memory[0xCD9D] == (-first)&255
            assert memory[0xCC7E] == memory[0xCD49] == second
            if step == 0:
                zero_steps.append(control)
        assert memory[0xC500:0xC546] == base[0xC500:0xC546]
        cases += 1
    report = dict(passed=True,prologue_cases=cases,all_control_bytes=True,
        call_targets_and_all_coefficients_checked=True,carry_from_neg_preserved_in_step_formula=True,
        zero_step_controls=zero_steps,point_loop_not_executed=True,coefficient_page_is_test_fixture=True,
        original_instructions=True,native_execution=False,irq_executed=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsPointRespawnDispatchVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
