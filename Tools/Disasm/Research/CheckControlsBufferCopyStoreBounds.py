"""Адресный разбор CopyScreenRows и отдельный стековый псевдоним родительского CALL.

Документация: ../../../Docs/ControlsBufferCopy.md#полная-область-собственных-записей
"""
from collections import Counter
from hashlib import sha256
import json
import re

from CheckControlsTextQueue import ROOT,base_memory
from CheckStationFlightCycle import DISK,ENTRIES
from CheckMapRaster import ObservedMemory
from ReferenceControlsTextDisplay import pixel_address
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC,SP,get_registers
from skoolkit.traceutils import disassemble

START,END,COUNTER,SAVED=0xC882,0xCA8D,0xCA84,0xCA8A


def analyze(rows,destination,count):
    """Источник символический, ни пиксель, ни входной SP не используется как экранный адрес."""
    by_pc={r['address']:r for r in rows}
    assert len(by_pc)==len(rows) and min(by_pc)==START and max(by_pc)==END-1
    hl=[('source',0),('destination',destination)]
    de=[None,None]
    active=0
    sp=('entry_SP',0)
    a,other_a=count,None
    remaining=None
    zero=None
    screen=[]
    patches=[]
    pushes=pops=0
    pc=START
    for _ in range(20000):
        assert pc in by_pc
        row=by_pc[pc]
        operation=re.sub(r'\s','',row['operation'])
        following=pc+len(bytes.fromhex(row['hex']))
        if operation=='LD(#CA8A),SP':
            assert pc==START and sp==('entry_SP',0)
            patches.extend((SAVED,SAVED+1))
        elif operation=='LD(#CA84),A':
            assert pc==0xC886 and isinstance(a,int) and 1<=a<=8
            remaining=a;patches.append(COUNTER)
        elif operation=='LDSP,HL':
            sp=hl[active]
        elif operation=='INCSP':
            sp=(sp[0],(sp[1]+1)&65535)
        elif match:=re.fullmatch(r'LDL,#([0-9A-F]{2})',operation):
            kind,value=hl[active]
            hl[active]=(kind,(value&0xFF00)|int(match[1],16))
        elif operation in ('POPAF','POPBC','POPDE','POPIX','POPIY'):
            assert sp[0]=='source'
            sp=(sp[0],(sp[1]+2)&65535);pops+=1
            if operation=='POPAF':a=None;zero=None
            if operation=='POPDE':de[active]=None
        elif operation in ('PUSHAF','PUSHBC','PUSHDE','PUSHIX','PUSHIY'):
            assert sp[0]=='destination'
            sp=(sp[0],(sp[1]-2)&65535)
            screen.extend((sp[1],(sp[1]+1)&65535));pushes+=1
        elif operation=="EXAF,AF'":
            a,other_a=other_a,a;zero=None
        elif operation=='EXX':
            active=1-active
        elif operation in ('SET4,L','RES4,L'):
            kind,value=hl[active]
            assert kind=='destination'
            hl[active]=(kind,value|16 if operation=='SET4,L' else value&0xFFEF)
        elif operation=='INCH':
            kind,value=hl[active];hl[active]=(kind,(value+256)&65535)
        elif operation=='LDDE,#F910':
            de[active]=0xF910
        elif operation=='ADDHL,DE':
            kind,value=hl[active]
            assert kind=='destination' and de[active]==0xF910
            hl[active]=(kind,(value+de[active])&65535)
        elif operation=='LDA,#00':
            assert pc==COUNTER-1 and isinstance(remaining,int)
            a=remaining
        elif operation=='DECA':
            assert pc==0xCA85 and isinstance(a,int)
            a=(a-1)&255;zero=a==0
        elif operation=='JPNZ,#C886':
            assert pc==0xCA86 and isinstance(zero,bool)
            if not zero:following=0xC886
        elif operation=='LDSP,#0000':
            assert pc==SAVED-1
            sp=('entry_SP',0)
        elif operation=='RET':
            assert pc==END-1 and sp==('entry_SP',0) and a==0 and active==0
            assert hl==[('source',count*256),('destination',destination+count*32)]
            assert pushes==pops==count*128
            assert Counter(patches)==Counter({SAVED:1,SAVED+1:1,COUNTER:count})
            return dict(screen_write_addresses=screen,code_write_addresses=patches,
                input_SP_restored_before_RET=True,push_instructions=pushes,pop_instructions=pops)
        else:
            raise AssertionError(('unsupported_address_operation',hex(pc),operation))
        pc=following
    raise AssertionError('bounded page loop did not terminate')


def parent_stack_alias(original):
    memory=ObservedMemory(original)
    # Подготовка допустимого для копировщика верхнего CPU-стека, его игровое происхождение не утверждается.
    memory[0xDB03:0xDB05]=[255,63]
    for address in range(0x8000,0x8C00):memory[address]=(address*37+(address>>8)*19)&255
    source=bytes(memory[0x8000:0x8C00])
    cpu=Simulator(memory,dict(PC=0xC870,SP=0xDB03,IY=0x5C3A))
    memory.writes=[];memory.recording=True
    for _ in range(10000):
        if cpu.registers[PC]==0x3FFF:break
        cpu.run()
    else:raise AssertionError('parent copy did not return')
    memory.recording=False
    assert cpu.registers[SP]==0xDB05
    for row in range(96):
        target=pixel_address(row,0)
        assert bytes(memory[target:target+32])==source[row*32:row*32+32]
    watched=[(address,value) for address,value in memory.writes if address in (0xDB01,0xDB02)]
    assert sorted(watched)==[(0xDB01,0x7C),(0xDB02,0xC8)]
    assert memory[0xDB01]+256*memory[0xDB02]==0xC87C
    return dict(entry=0xC870,input_SP=0xDB03,call_pc=0xC879,return_address=0xC87C,
        final_SP=0xDB05,bank1_length_operand_written=0xC87C,write_addresses=[0xDB01,0xDB02],
        complete_copy_and_return_executed=True,prepared_external_stack=True,natural_game_caller_proved=False)


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(DISK).hexdigest()==manifest['sha256']
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    rows=[r for g in flow if g['name']=='Controls' for r in g['instructions']
        if r['slot']==22 and START<=r['address']<END]
    original=base_memory()
    assert len(rows)==416
    parent_offset=ENTRIES[22]['offset']+0x870
    assert bytes(original[0xC870:0xC882])==DISK[parent_offset:parent_offset+18]
    for row in rows:
        pc=row['address'];raw=bytes.fromhex(row['hex']);offset=ENTRIES[22]['offset']+row['offset']
        assert DISK[offset:offset+len(raw)]==raw==bytes(original[pc:pc+len(raw)])
        text,size=disassemble(original,pc)
        assert size==len(raw) and re.sub(r'\s','',text.replace('$','#'))==re.sub(r'\s','',row['operation'])
    profiles=[]
    union=set()
    # Проверка всех 108 непустых интервалов символьных строк внутри одной трети.
    for third in range(3):
        for row in range(8):
            for count in range(1,9-row):
                destination=0x400F+third*2048+row*32
                result=analyze(rows,destination,count)
                wanted=[pixel_address(third*64+row*8+y,0)+x for y in range(count*8) for x in range(32)]
                assert Counter(result['screen_write_addresses'])==Counter(wanted)
                assert len(set(wanted))==256*count
                assert all(0x4000<=a<0x5800 for a in wanted)
                assert not ({0xDB01,0xDB02}&set(result['screen_write_addresses']+result['code_write_addresses']))
                union.update(wanted)
                profiles.append(dict(third=third,first_character_row=row,pages=count,
                    destination=destination,screen_bytes=len(wanted),code_store_count=count+2))
    assert len(profiles)==108 and union==set(range(0x4000,0x5800))
    # Неправильный экранный адрес должен выявить пересечение, а POP HL отвергается как источник адреса из пикселей.
    danger=analyze(rows,0xDB0F,1)
    assert {0xDB01,0xDB02}<=set(danger['screen_write_addresses'])
    altered=[dict(row) for row in rows]
    first=next(row for row in altered if re.sub(r'\s','',row['operation'])=='POPBC')
    first['operation']='POP HL';first['hex']='e1'
    try:analyze(altered,0x400F,1)
    except AssertionError:pass
    else:raise AssertionError('pixel word accepted as address')
    alias=parent_stack_alias(original)
    result=dict(passed=True,original_disk_sha256=manifest['sha256'],entry=START,end_exclusive=END,
        original_code_bytes=END-START,original_code_sha256=sha256(bytes(original[START:END])).hexdigest(),
        parent_code_sha256=sha256(bytes(original[0xC870:0xC882])).hexdigest(),
        registered_instructions=len(rows),address_domain_profiles=profiles,profile_count=len(profiles),
        source_page_base_symbolic=True,pixel_words_do_not_feed_address_registers=True,
        input_SP_not_used_for_worker_push_destinations=True,worker_screen_physical_bank=5,
        screen_union_start=0x4000,screen_union_end_exclusive=0x5800,screen_union_bytes=len(union),
        code_physical_bank=1,code_write_addresses=[COUNTER,SAVED,SAVED+1],
        worker_own_writes_disjoint_from_bank1_DB01_DB02=True,
        out_of_contract_destination_reaches_DB01_DB02=True,POP_HL_negative_control_rejected=True,
        parent_stack_alias=alias,worker_execution_models_rerun=False,
        caller_stack_domains_and_all_runtime_modifications_proved=False,
        natural_temporary_module_length_writer_proved=False,IRQ_executed=False,native_execution=False,assembly_executed=False)
    path=ROOT/'Tools/Disasm/Reports/ControlsBufferCopyStoreBoundsVerification.json'
    if path.exists():assert json.loads(path.read_bytes())==result
    else:path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('108 символических областей C882, все пиксели независимы от адресов, отдельный CALL C879 пишет C87C при SP=DB03')


if __name__=='__main__':
    main()
