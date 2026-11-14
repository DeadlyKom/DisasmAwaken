"""Продолжение условного хвоста через настоящий 6000, стек 7FFD и границу очищенного буфера."""
import json
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory,payload
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckActionTextQueueCalls import Ports
from CheckScreenUpdate import PortTrace, put


def check_rom_returns(simulator):
    memory, registers = simulator.memory, simulator.registers
    rom = bytes(memory.roms[1])
    ports = PortTrace(simulator)
    simulator.set_tracer(ports)
    returns = []
    memory.writes = []
    memory.recording = True
    for _ in range(120):
        pc = registers[PC]
        if pc == 0xCDE7:
            break
        assert pc < 0x4000 and memory.o7ffd == 0x10
        if pc == 0x062D:
            # Проверка фактического писателя нового RST в ACTION.
            write_count = len(memory.writes)
            assert memory[0xCDE8] == 0x3A
            simulator.run()
            assert memory.writes[write_count:] == [(0, 0xCDE8 - 0xC000, 0xFF)]
            continue
        if memory[pc] != 0xC9:
            simulator.run()
            continue
        # Проверка адреса RET из физического ПЗУ, CALL не мог сохранить слово в этой области.
        sp = registers[SP]
        target = int.from_bytes(rom[sp:sp + 2], 'little')
        simulator.run()
        assert registers[PC] == target and registers[SP] == sp + 2
        returns.append((pc, sp, target))
    else:
        raise AssertionError('ПЗУ не вышло по CDE7')
    assert returns == [(0x3895, 0x1812, 0x0620), (0x2C01, 0x1814, 0xCDE7)]
    assert ports.writes == [(0xFFFD, 7), (0xFFFD, 14)]
    assert (0, 0xCDE8 - 0xC000, 0xFF) in memory.writes
    assert bytes(memory[0xCDE6:0xCDE9]) == bytes.fromhex('DD 67 FF')
    # Исполнение с середины прежней LD IXH,A, затем изменённый байт вызывает ещё один RST 38.
    simulator.run()
    assert registers[PC] == 0xCDE8 and registers[SP] == 0x1816
    simulator.run()
    memory.recording = False
    assert registers[PC] == 0x0038 and registers[SP] == 0x1814
    assert bytes(memory.roms[1]) == rom and memory.o7ffd == 0x10
    return dict(rom_returns=returns, first_bank0_entry=0xCDE7, changed_opcode_address=0xCDE8, opcode_writer=0x062D,
                changed_opcode=0xFF, repeated_rom_entry=0x0038, repeated_rom_sp=0x1814)


def main():
    flat=flat_action();baseline=[bytearray(16384) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):baseline[bank][:]=bytes(flat[start:start+16384])
    baseline[1][:]=bytes(base_memory()[0xC000:]);template=payload(23)[:0x13B]
    # Адрес соответствует пяти внутренним совпадениям старого фрагмента, фактический игровой перенос не предполагается.
    fixture=0x5DA0;cases=[]
    for pattern in (0,0x55,0xA5):
        for saved_stack in (0x3FFE,0x4FFE,0x5FA0):
            memory=RecordedBanks(banks=[b.copy() for b in baseline],out7ffd=17)
            memory.banks[1][0x2000:]=memory.banks[5][0x2000:]
            memory.banks[6][:0x3400]=memory.banks[2][0xC00:]
            memory.banks[2][:0xC00]=bytes([pattern])*0xC00
            put(memory,fixture,template);put(memory,0x5E33,saved_stack.to_bytes(2,'little'))
            output_word=baseline[1][0x17A2]+256*baseline[1][0x17A3]
            expected_HL=((-output_word)&65535)|32768 if output_word&32768 else output_word
            simulator=Simulator(memory);simulator.registers[:]=get_registers({'PC':fixture+0x4B,'SP':0x6000,
                'HL':0x1357,'DE':0x2468,'BC':0x3579,'AF':0x5A5D,'IX':0xA100,'IY':0x5678,
                '^HL':0x6789,'^DE':0x789A,'^BC':0x89AB,'^AF':0x9ABC},None,False)
            ports=Ports(memory);simulator.set_tracer(ports);boundaries=[]
            for steps in range(100000):
                pc=simulator.registers[PC]
                if pc in (0x6000,0xEC56,0x7FFD,0x8001):
                    boundaries.append(dict(pc=pc,sp=simulator.registers[SP],hl=simulator.registers[6]*256+simulator.registers[7],
                        instruction_bytes=bytes(memory[pc:pc+3]).hex()))
                    if pc==0x8001:break
                simulator.run()
            else:raise AssertionError(('граница не достигнута',hex(pc)))
            assert [r['pc'] for r in boundaries]==[0x6000,0xEC56,0x7FFD,0x8001]
            assert boundaries[0]['sp']==0x5FFE and boundaries[0]['hl']==0,boundaries
            assert boundaries[1]['instruction_bytes']==bytes(flat[0x6C56:0x6C59]).hex()
            assert boundaries[1]['instruction_bytes']!=bytes(baseline[1][0x2C56:0x2C59]).hex()
            assert boundaries[2]['hl']==expected_HL and boundaries[2]['instruction_bytes']=='f9dd77'
            assert boundaries[3]['sp']==expected_HL and memory[0x8001]==255
            assert bytes(memory[0x7FFE:0x8001])==bytes.fromhex('dd77ff')
            assert simulator.registers[8:12]==[255]*4 and memory[0xFFFE]==16
            assert ports.events==[(0x7FFD,22),(0x7FFD,16),(0x7FFD,17),(0x7FFD,17),(0x7FFD,16)]
            assert bytes(memory[0x5E33:0x5E35])==saved_stack.to_bytes(2,'little')
            # Проверка RST, запись адреса возврата приходится на недоступное для записи ПЗУ.
            rom_bytes = memory[expected_HL - 2:expected_HL]
            simulator.run()
            assert simulator.registers[PC] == 0x0038 and simulator.registers[SP] == expected_HL - 2
            assert memory[expected_HL - 2:expected_HL] == rom_bytes and memory.o7ffd == 0x10
            rom_entry, rom_entry_sp = simulator.registers[PC], simulator.registers[SP]
            continuation = check_rom_returns(simulator)
            cases.append(dict(initial_bitmap=pattern,saved_SP=saved_stack,boundaries=boundaries,
                        indexed_write_address=0xFFFE,indexed_write_value=16,
                        rom_entry=rom_entry,rom_entry_sp=rom_entry_sp,
                        rst_return_address=0x8002,rst_return_word_stored=False,rom_continuation=continuation))
    result=dict(passed=True,total_cases=len(cases),cases=cases,address_consistent_fixed_fixture=fixture,
        real_tail_clear_viewport_and_queue_wrapper_paging_executed=True,original_backup_core_6000_restored=True,
        bank1_E000_FFFF_backup_overwrites_actual_EC56_queue_consumer=True,
        EC56_executes_original_core_bytes_from_6C56_instead_of_queue=True,
        final_HL_reads_bank1_word_D7A2_not_original_Action_output=True,
        continuation_at_7FFD_sets_SP_to_final_HL=True,observed_new_SP=expected_HL,
        cleared_8000_byte_changes_indexed_displacement_from_26_to_FF=True,
        next_8001_byte_is_RST38=True,rst_executed_to_rom_entry=True,
        original_128k_basic_rom_executed=True,port_input_profile='default_ff',
        stopped_at_second_rom_entry=True,
        legitimate_game_entry_relocation_and_temporary_payload_proved=False,
        changing_backup_core_by_temporary_payload_not_excluded=True,
        complete_register_RAM_write_multiplicity_R_T_proof=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsTemporaryModuleResumeVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
