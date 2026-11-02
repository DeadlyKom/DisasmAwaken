"""Полный AC5D, каждый байт каждого поля, пятнадцать действительных записей в выбранном банке 0."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh

DESTINATIONS = ((0,0xF79C),(2,0xF798),(3,0xA968),(4,0x63B9),(5,0xA8B5),
    (6,0x7B6B),(6,0x6874),(7,0x6615),(8,0xE6E7),(9,0xE823),
    (10,0x65E5),(11,0x79A4),(12,0x7E07),(13,0x7E09),(14,0x7DE4))


def main():
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original = base_memory()
    # Представление выбранного банка 0, ядро действительно перенесено из 623D в 6000.
    original[0x6000:0x10000] = source
    original[0x6000:0x7F8F] = source[0x23D:0x21CC]
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    cases = 0
    for field in range(15):
        for value in range(256):
            memory.recording = False
            for address in touched:
                memory[address] = original[address]
            data = [(73*value+17*i+field)&255 for i in range(15)]
            data[field] = value
            memory[0x9BA4:0x9BB3] = data
            memory[0xBFFE:0xC000] = [0xFF,0x3F]
            initial = get_registers({'AF':0xA500|((73*field+value)&255),'HL':0x1357,'DE':0x2468,
                'BC':0x369C,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
                'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xAC5D},None,False)
            initial[14],initial[15],initial[26],initial[27] = value,(field*value+127)&255,value&1,field%3
            wanted = list(initial)
            wanted[0],wanted[6],wanted[7],wanted[SP],wanted[15] = data[14],0x9B,0xB2,0xC000,refresh(initial[15],46)
            writes = [(address,data[index]) for index,address in DESTINATIONS]
            expected = list(memory)
            for address,new_value in writes:
                expected[address] = new_value
            simulator.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(60):
                if simulator.registers[PC]==0x3FFF:
                    break
                simulator.run()
            else:
                raise AssertionError(('возврат',field,value))
            memory.recording = False
            compared = (*range(13),14,15,*range(16,24),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared), (field,value,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert memory==expected and Counter(memory.writes)==Counter(writes), (field,value)
            touched = {address for address,_ in writes}
            cases += 1
    report = dict(passed=True,total_cases=cases,all_field_byte_values=True,selected_bank=0,
        ignored_field_index=1,duplicated_field_index=6,actual_destination_writes=15,
        exact_registers_flags_r_and_sp=True,every_ram_byte_and_write_checked=True,
        original_action_core_relocation=True,game_field_names_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionApplyParametersVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
