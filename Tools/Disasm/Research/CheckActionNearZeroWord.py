"""6EAC, исходный JR NC сохраняется, полный знаковый диапазон и точные обмены AF."""
from collections import Counter
from functools import lru_cache
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh


@lru_cache(maxsize=None)
def cost(start,end):
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    return sum(2 if i['hex'][:2] in ('cb','ed','dd','fd') else 1
        for i in next(r for r in flow if r['name']=='Action')['instructions'] if start<=i['address']<end)


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory)
    touched=set();counts=Counter()

    def check(word,control,alt_af,kind):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=original[address]
        memory[0xA78F:0xA791]=[word&255,word>>8]
        memory[0x6EAD],memory[0x669F]=control,(word^alt_af)&255
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':alt_af,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6EAC},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);writes=[];m1=cost(0x6EAC,0x6EB0)
        if not control:
            wanted[0:2]=[0,0x54]
            path='disabled'
        else:
            signed=word if word<0x8000 else word-0x10000
            magnitude=abs(signed);difference=(magnitude-2)&65535
            result=(-difference)&65535 if signed<0 else difference
            wanted[2:4]=[0,2];wanted[6:8]=[result>>8,result&255]
            writes.append((0x669F,control))
            if signed<0:
                saved_a=(~(difference>>8))&255
                wanted[16:18]=[saved_a,0x92|(saved_a&0x28)]
            else:
                wanted[16:18]=[control,0x54|((word>>8)&0x28)]
            m1+=cost(0x6EB0,0x6EBA)+cost(0x6EC1,0x6ECB)+cost(0x6ED2,0x6ED5)
            if signed<0:m1+=cost(0x6EBA,0x6EC1)+cost(0x6ECB,0x6ED2)
            if magnitude<2:
                wanted[0:2]=[initial[16],sub16_flags(magnitude,2)]
                writes.extend([(0xA78F,result&255),(0xA790,result>>8)])
                m1+=cost(0x6ED5,0x6ED9);path='word_written'
            else:
                wanted[0:2]=[0,0x44]
                writes.append((0x6EAD,0));m1+=cost(0x6ED9,0x6EDE);path='disabled_after_compare'
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        expected=list(memory)
        for address,value in writes:expected[address]=value
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(38):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',word,control,alt_af))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(word,control,alt_af,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(word,control,alt_af,path)
        touched={address for address,_ in writes};counts[kind]+=1

    # Проверка всех слов при выключенной обработке и двух различных ненулевых кодах включения.
    for word in range(65536):
        for control in (0,1,255):check(word,control,word,'words')
    print('All words and three control profiles complete',flush=True)
    # Проверка каждого кода включения на всех особых ветвях и краях знакового диапазона.
    for control in range(256):
        for word in (0,1,0xFFFF,2,0xFFFE,0x7FFF,0x8000):check(word,control,(control*257)&65535,'controls')
    # Проверка всех альтернативных AF на путях записи, сброса и отрицательного слова.
    for alt_af in range(65536):
        for word in (1,2,0xFFFF):check(word,1,alt_af,'alternative_af')
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        all_signed_words=True,all_control_bytes=True,all_alternative_af_words=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
        no_cpu_stack_writes=True,word_written_only_for_original_values=[0,1,65535],
        transformed_words={'0000':'FFFE','0001':'FFFF','FFFF':'0001'},
        magnitude_ge_two_clears_control_without_writing_word=True,
        original_jr_nc_preserved=True,all_joint_inputs_exhausted=False,
        game_meaning_of_source_word_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearZeroWordVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
