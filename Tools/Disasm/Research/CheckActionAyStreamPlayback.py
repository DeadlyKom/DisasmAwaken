"""Последовательное исполнение девяти исходных потоков по настоящим адресам до маркера."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from ActionAyStreams import STREAMS
from CheckActionParameterActivation import flat_action
from CheckActionAyEffects import AyLatch
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def main():
    flat=flat_action();counts=Counter();ticks=0
    for name,start,count in STREAMS:
        for channel in (0,1):
            for initial_mixer in (0,0x55,0xFF):
                memory=Memory(flat);simulator=Simulator(memory);trace=AyLatch(initial_mixer);simulator.set_tracer(trace)
                memory[0xECA9:0xECAB]=[0,0];memory[0xECF6:0xECF8]=[0,0]
                operand=0xECF6 if channel else 0xECA9;memory[operand:operand+2]=[start&255,start>>8]
                memory[0xED83]=0;memory[0xBFFE:0xC000]=[255,63];wanted_mixer=initial_mixer
                for row in range(count+1):
                    expected=list(memory);writes=[];events=[]
                    def byte(address,value):expected[address]=value;writes.append((address,value))
                    def select(reg):events.append((0xFFFD,reg))
                    def output(value,outi=False):events.append((0xBEFD if outi else 0xBFFD,value))
                    # Расчёт событий очередной исходной строки, дополнительный вызов после маркера не читает поток.
                    if row<count:
                        address=start+4*row;lo,hi,control,volume=flat[address:address+4]
                        select(channel*2);output(lo,True);select(channel*2+1);output(hi,True);select(7)
                        wanted_mixer=(wanted_mixer&(0xED if channel else 0xF6))|(((control<<1)|(control>>7))&255 if channel else control)
                        output(wanted_mixer);select(8+channel);output(volume,True)
                        next_address=address+4;byte(operand,next_address&255);byte(operand+1,next_address>>8)
                        if row+1==count:
                            assert flat[next_address]==0;byte(operand+1,0);select(7)
                            wanted_mixer|=0x12 if channel else 9;output(wanted_mixer)
                    select(5);output(12);select(7);wanted_mixer=(wanted_mixer&0xDB)|32;output(wanted_mixer)
                    select(6);output(5);select(10);output(4)
                    initial=get_registers({'DE':0x2468,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xECA8},None,False)
                    initial[15]=0x80;simulator.registers[:]=initial;trace.events=[];trace.reads=[];memory.writes=[];memory.recording=True
                    for _ in range(150):
                        if simulator.registers[PC]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError('возврат')
                    memory.recording=False
                    assert memory==expected and memory.writes==writes,(name,channel,row)
                    assert trace.events==events and trace.mixer==wanted_mixer,(name,channel,row,trace.events,events)
                    assert simulator.registers[SP]==0xC000
                    ticks+=1
                counts[name]+=1
    report=dict(passed=True,sequences=sum(counts.values()),ticks=ticks,streams=len(STREAMS),physical_frames=sum(s[2] for s in STREAMS),
        physical_stream_bytes=sum(4*s[2]+1 for s in STREAMS),both_channels=True,original_stream_addresses_used=True,
        full_streams_to_marker_and_one_disabled_tick=True,every_memory_write_and_port_checked=True,
        actual_ay_hardware_executed=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionAyStreamPlaybackVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
