"""Продолжение условного хвоста через настоящий 6000, стек 7FFD и границу очищенного буфера."""
import json
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory,payload
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckActionTextQueueCalls import Ports
from CheckScreenUpdate import put


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
            cases.append(dict(initial_bitmap=pattern,saved_SP=saved_stack,boundaries=boundaries,
                        indexed_write_address=0xFFFE,indexed_write_value=16,stopped_before_RST38=True))
    result=dict(passed=True,total_cases=len(cases),cases=cases,address_consistent_fixed_fixture=fixture,
        real_tail_clear_viewport_and_queue_wrapper_paging_executed=True,original_backup_core_6000_restored=True,
        bank1_E000_FFFF_backup_overwrites_actual_EC56_queue_consumer=True,
        EC56_executes_original_core_bytes_from_6C56_instead_of_queue=True,
        final_HL_reads_bank1_word_D7A2_not_original_Action_output=True,
        continuation_at_7FFD_sets_SP_to_final_HL=True,observed_new_SP=expected_HL,
        cleared_8000_byte_changes_indexed_displacement_from_26_to_FF=True,
        next_8001_byte_is_RST38=True,stopped_before_ROM_execution=True,
        legitimate_game_entry_relocation_and_temporary_payload_proved=False,
        changing_backup_core_by_temporary_payload_not_excluded=True,
        complete_register_RAM_write_multiplicity_R_T_proof=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsTemporaryModuleResumeVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
