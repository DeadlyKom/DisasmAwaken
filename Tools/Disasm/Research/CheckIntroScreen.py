"""Независимый экранный декодер, все группы и обе стороны ссылок, полный CPU/RAM/стек."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT
from Analyze import payload
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionUnpack import RecordedFlat
from IntroScreenCodec import Writer,decode,physical


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.read_bytes()
    assert len(rom)==16384 and rom[0x1FC6:0x1FC9]==bytes((0xE1,0xC8,0xE9))
    original=payload(3);code=original[0x2631:0x26CB];assert len(code)==154
    baseline=[0xA5]*65536;baseline[:16384]=rom
    totals=Counter();groups=Counter();seen_flags=set();cases=0;original_hash=None

    def check(data,kind):
        nonlocal cases,original_hash
        expected=decode(data);output=expected['data'];size=len(output)
        flags=cases&255;seen_flags.add(flags)
        stack=(0xBFFE,0xA0FE,0x5FFE)[cases%3]
        initial_hl=(0,0x1357,0xFFFF)[cases%3]
        m=RecordedFlat(baseline);m[0x6E31:0x6ECB]=code;m[0x6ECB:0x6ECB+len(data)]=data
        m[stack:stack+2]=[255,63]
        initial=get_registers({'AF':((cases*73)&255)*256+flags,'HL':initial_hl,
            'DE':0x2468,'BC':0x369C,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            '^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x6E31},None,False)
        initial[14],initial[26],initial[27]=flags,cases&1,cases%3
        wanted_memory=list(m);writes=[]

        def put(address,value):
            wanted_memory[address]=value;writes.append((address,value))

        def push(value):
            put(stack-1,value>>8);put(stack-2,value&255)

        push(0x6E3C)
        sources=[None]*size;starts={r['position']:r for r in expected['references']}
        cursor=(initial_hl+1)&65535;position=1
        # Расчёт рабочего HL после прямых/обратных ссылок и буквальных выборок.
        while position<size:
            reference=starts.get(position)
            if reference:
                start=position+reference['offset'];direction=-1 if reference['reverse'] else 1
                for index in range(reference['length']):sources[position+index]=start+direction*index
                cursor=(0x4000+start+direction*reference['length'])&65535
                position+=reference['length']
            else:cursor=(cursor-1)&65535;position+=1
        # Расчёт всех экранных записей и временных PUSH AF для адресов атрибутов.
        for index,value in enumerate(output):
            source_index=sources[index]
            if source_index is not None and source_index>=6144:
                high=(0x4000+source_index)>>8
                cp_flags=0x4A if high==0x58 else 0x0A
                source_flags=(cp_flags&0xC4)|(high&0x28)|1
                push(high*256+source_flags)
            logical=0x4000+index
            if logical>=0x5800:
                high=logical>>8;push(high*256+(0x4A if high==0x58 else 0x0A))
            put(physical(logical),value)
        last=0x4000+size-1;last_physical=physical(last)
        map_a=(last>>8) if last>=0x5800 else last_physical&255
        map_carry=0 if last>=0x5800 else (last>>6)&1
        reservoir=expected['bit_buffer']|(1<<(7-expected['remaining_bits']))
        wanted=list(initial)
        wanted[0:8]=[255,0xA8,last_physical>>8,last_physical&255,
            (0x4000+size)>>8,(0x4000+size)&255,cursor>>8,cursor&255]
        wanted[9]=255;wanted[16:24]=[map_a,0x50|map_carry,0,0xC0,reservoir,0x8F,0x27,0x58]
        wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator=Simulator(m);simulator.registers[:]=initial;m.writes=[];m.recording=True
        simulator.run(start=0x6E31,stop=0x3FFF);m.recording=False
        # Проверка всех регистров кроме R и всех записей по независимому битовому разбору.
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(kind,cases,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert list(m)==wanted_memory,(kind,cases,'RAM',[(hex(i),a,b) for i,(a,b) in enumerate(zip(m,wanted_memory)) if a!=b][:12])
        assert Counter(writes)==Counter(m.writes),(kind,cases,'writes',
            (Counter(writes)-Counter(m.writes)).most_common(8),(Counter(m.writes)-Counter(writes)).most_common(8))
        if kind=='original':
            digest=hashlib.sha256(bytes(m[0x4000:0x5B00])).hexdigest()
            if original_hash is None:original_hash=digest
            assert digest==original_hash=='3bb10a9f778e0da7f2529d5572ec5c0146f275746a6ac001670eb377ad01d58b'
        totals[kind]+=1;groups.update(expected['groups']);cases+=1

    for _ in range(8):check(original[0x26CB:],'original')
    check_data=Writer();check_data.literal(0xA7,first=True);check_data.end();check(bytes(check_data.data),'single_literal')
    # Проверка всех 23 групп длины и смещения, включая обратное копирование.
    for length_code in range(0xE9,0x100):
        for offset_high in range(0xE9,0x100):
            for reverse in (False,True):
                extension=1
                base_length=256 if length_code==0xF9 else (256-length_code if length_code<0xF9 else 257-length_code)
                length=(base_length+(offset_high<0xFD)-1)%256+1
                low=(cases*73)&255;offset=offset_high*256+low-65536
                prefix=-offset+(length-1 if reverse else 0)
                writer=Writer()
                for index in range(prefix):writer.literal((index*37+cases*53)&255,first=index==0)
                writer.bit(0);writer.group(length_code)
                if length_code==0xF9:writer.byte(extension)
                writer.group(offset_high);writer.bit(int(reverse));writer.byte(low);writer.end()
                check(bytes(writer.data),'group_combinations')
        if (length_code-0xE9)%4==0:print('Группы до '+format(length_code,'02X')+' проверены',flush=True)
    # Проверка всех ненулевых расширений длины и нулевого расширения как терминатора.
    for extension in range(1,256):
        writer=Writer();writer.literal(extension,first=True)
        writer.match(257-extension,-1,extended=True);writer.end()
        check(bytes(writer.data),'extended_lengths')
    assert seen_flags==set(range(256))
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(totals),group_coverage=dict(groups),
        original_physical_screen_sha256=original_hash,original_screen_bytes=6912,
        original_stream_bytes_consumed=decode(original[0x26CB:])['stream_position'],
        all_23_length_and_offset_groups=True,both_reference_directions=True,
        all_nonzero_extension_values=True,byte_length_wrap_preserved=True,
        all_initial_flags_values_across_fixtures=True,all_registers_except_R=True,
        full_logical_RAM_including_stack=True,write_multiplicity_proved=True,
        independent_bitstream_decoder=True,rom_call_stubbed=False,rom_bytes_1FC6='E1C8E9',
        rom_name=args.rom.name,rom_sha256=hashlib.sha256(rom).hexdigest(),
        arbitrary_invalid_streams_proved=False,physical_banks_separately_proved=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroScreenVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='group_coverage'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
