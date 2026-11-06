"""ECA8, два четырёхбайтовых потока и регистры канала C, независимый эталон портов и состояния."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


class AyLatch:
    def __init__(self,mixer):self.selected=0;self.mixer=mixer;self.events=[];self.reads=[]
    def write_port(self,registers,port,value,offset):
        self.events.append((port,value))
        if port==0xFFFD:self.selected=value
        elif port in (0xBFFD,0xBEFD) and self.selected==7:self.mixer=value
    def read_port(self,registers,port):
        assert port==0xFFFD and self.selected==7
        self.reads.append((port,self.mixer));return self.mixer


def cp4(value):
    result=(value-4)&255
    return (result&128)|(64 if result==0 else 0)|(16 if (value&15)<4 else 0)|(4 if ((value^4)&(value^result)&128) else 0)|2|(1 if value<4 else 0)


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();touched=set()
    def cost(start,end):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(start,end,'h'))
    active_a,stop_a=cost(0xECA8,0xECE4),cost(0xECE4,0xECF5)
    active_b,stop_b=cost(0xECF5,0xED35),cost(0xED35,0xED46)
    sample_cost=cost(0xED46,0xED5C);tail_cost=cost(0xED46,0xED8F)-2
    def check(r=0,mixer=255,amplitude=0,active=3,ends=3,control_a=0,control_b=0,pointer_a=0x9000,pointer_b=0x9100):
        nonlocal touched
        memory.recording=False
        for address in touched:memory[address]=baseline[address]
        cursor_a=pointer_a if active&1 else 0x37;cursor_b=pointer_b if active&2 else 0x91
        memory[0xECA9:0xECAB]=[cursor_a&255,cursor_a>>8];memory[0xECF6:0xECF8]=[cursor_b&255,cursor_b>>8]
        memory[pointer_a:pointer_a+5]=[0x14,0x23,control_a,0x0A,0 if ends&1 else 7]
        memory[pointer_b:pointer_b+5]=[0x36,0x45,control_b,0x0B,0 if ends&2 else 9]
        memory[0xED83]=amplitude;memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':0xA5FF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xECA8},None,False)
        initial[14],initial[15],initial[26],initial[27]=counts.total()&255,r,counts.total()&1,counts.total()%3
        wanted=list(initial);expected=list(memory);writes=[];events=[];reads=[];mixer_value=mixer
        def byte(address,value):expected[address]=value;writes.append((address,value))
        def select(reg):events.append((0xFFFD,reg))
        def output(value,outi=False):events.append((0xBEFD if outi else 0xBFFD,value))
        m1=0
        # Обновление двух каналов по физическим байтам строки, без исполнения машинных инструкций в эталоне.
        for channel,cursor,enabled,ending,control,low,high,volume in (
            (0,cursor_a,active&1,ends&1,control_a,0x14,0x23,0x0A),
            (1,cursor_b,active&2,ends&2,control_b,0x36,0x45,0x0B)):
            if not enabled:m1+=4;continue
            select(channel*2);output(low,True);select(channel*2+1);output(high,True)
            select(7);reads.append((0xFFFD,mixer_value))
            mixer_value=(mixer_value&(0xED if channel else 0xF6))|(((control<<1)|(control>>7))&255 if channel else control)
            output(mixer_value);select(8+channel);output(volume,True)
            following=cursor+4;operand=0xECF6 if channel else 0xECA9
            byte(operand,following&255);byte(operand+1,following>>8)
            m1+=active_b if channel else active_a
            if ending:
                byte(operand+1,0);select(7);reads.append((0xFFFD,mixer_value))
                mixer_value|=0x12 if channel else 9;output(mixer_value);m1+=stop_b if channel else stop_a
        # Расчёт значения R именно в момент LD A,R, включая два M1 этой инструкции.
        sampled=refresh(r,m1+sample_cost);noise=32 if sampled>=32 else 0
        select(5);output(12);select(7);reads.append((0xFFFD,mixer_value))
        mixer_value=(mixer_value&0xDB)|noise;output(mixer_value)
        select(6);output(5);select(10);output(max(4,amplitude>>1))
        m1+=tail_cost+int(sampled>=32)+int((amplitude>>1)<4)
        wanted[0:2]=[max(4,amplitude>>1),cp4(amplitude>>1)];wanted[2:4]=[0xBF,0xFD]
        wanted[6:8]=[((cursor_b+4)>>8) if active&2 else 0,noise]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(r,m1)
        simulator.registers[:]=initial;trace=AyLatch(mixer);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(150):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат')
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(r,mixer,amplitude,active,ends,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==writes,(r,mixer,amplitude,active,ends,memory.writes,writes)
        assert trace.events==events and trace.reads==reads and trace.mixer==mixer_value,(trace.events,events)
        touched={a for a,_ in memory.writes};counts[str(active)+':'+str(ends)]+=1
    # Проверка всех входных R, всех режимов активности и завершения потоков, всех байтов параметра канала C.
    for r in range(256):
        for active in range(4):
            for ends in range(4):check(r=r,active=active,ends=ends,amplitude=r,control_a=r,control_b=r^255)
    for amplitude in range(256):
        for mixer in range(256):check(amplitude=amplitude,mixer=mixer,r=(amplitude+mixer)&255,control_a=mixer,control_b=amplitude)
    # Проверка всех битовых рисунков строк при сохранении чужих каналов в прочитанном смесителе.
    for control in range(256):
        for active in (1,2,3):
            for ends in range(4):check(active=active,ends=ends,control_a=control,control_b=control,mixer=control^255)
    # Проверка переноса младшего байта курсора через границу страницы общей RAM.
    for offset in (0xFC,0xFD,0xFE,0xFF):
        for ends in range(4):check(pointer_a=0x9200+offset,pointer_b=0x9400+offset,ends=ends)
    report=dict(passed=True,total_cases=counts.total(),cases_by_paths=dict(counts),
        method='independent_stream_mixer_port_and_refresh_oracle_against_original_instructions',
        all_r_and_amplitude_bytes=True,all_mixer_bytes=True,all_control_byte_patterns=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,exact_ports_and_reads_checked=True,
        outi_befd_mirror_observed=True,maximum_additional_stack_bytes=0,
        ay_readback_model='selected_register7_eight_bit_latch',real_ay_hardware_executed=False,
        stream_end_tests_next_tone_low_byte=True,channel_c_uses_r_threshold_not_single_bit=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionAyEffectsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
