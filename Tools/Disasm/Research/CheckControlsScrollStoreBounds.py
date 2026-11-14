"""Статическое множество всех собственных записей ScrollTextWindow.

Документация: ../../../Docs/ControlsTextDisplay.md#полная-область-записей-прокрутки
"""
from collections import Counter
from hashlib import sha256
import json

from CheckControlsTextQueue import ROOT,base_memory
from CheckControlsTextDisplay import execute
from CheckStationFlightCycle import DISK,ENTRIES
from ReferenceControlsTextDisplay import initialize,pixel_address

START,END,SAVED=0xED28,0xEFC4,0xEFC1


def analyze(memory,rows):
    """Разбор единственной линейной цепочки, значения загруженных пикселей не влияют на SP."""
    stack=None
    screen=[]
    stores=[]
    pops=pushes=stack_loads=0
    assert rows[0]['address']==START and rows[-1]['address']==END-1
    position=START
    for row in rows:
        pc=row['address'];size=len(bytes.fromhex(row['hex']))
        assert pc==position
        raw=bytes(memory[pc:pc+size]);position+=size
        if pc==START:
            assert raw==bytes.fromhex('ed73c1ef')
            stores.extend((SAVED,SAVED+1))
        elif raw[0]==0x31:
            assert size==3
            stack_loads+=1
            if pc==SAVED-1:
                # Префикс меняет ровно два байта этого операнда на входной SP.
                assert pc==END-4
                stack='entry_SP'
            else:
                stack=int.from_bytes(raw[1:],'little')
        elif raw[0] in (0xC1,0xD1,0xE1,0xF1):
            assert size==1 and isinstance(stack,int)
            stack=(stack+2)&65535;pops+=1
        elif raw[0] in (0xC5,0xD5,0xE5,0xF5):
            assert size==1 and isinstance(stack,int)
            stack=(stack-2)&65535;screen.extend((stack,(stack+1)&65535));pushes+=1
        elif raw[0]==0xD9:
            assert size==1
        elif raw[0] in (0x11,0x21):
            assert size==3
        elif raw==b'\xC9':
            assert pc==END-1 and stack=='entry_SP'
        else:
            raise AssertionError(('unsupported_instruction',hex(pc),raw.hex()))
    assert position==END and (pops,pushes,stack_loads)==(180,216,67)
    return dict(screen_write_addresses=screen,code_write_addresses=stores,
        pop_instructions=pops,push_instructions=pushes,LD_SP_immediates=stack_loads,
        original_input_SP_restored_before_RET=True,no_conditional_or_external_control=True)


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(DISK).hexdigest()==manifest['sha256']
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    rows=[r for g in flow if g['name']=='Controls' for r in g['instructions']
        if r['slot']==23 and START<=r['address']<END]
    original=base_memory()
    for row in rows:
        pc=row['address'];raw=bytes.fromhex(row['hex']);offset=ENTRIES[23]['offset']+row['offset']
        assert DISK[offset:offset+len(raw)]==raw==bytes(original[pc:pc+len(raw)])
    assert len(rows)==527
    initial=analyze(original,rows)
    expected=list(original);initialize(expected)
    initialized=list(original);execute(initialized,0xEC0E)
    assert initialized[0xC000:]==expected[0xC000:]
    prepared=analyze(initialized,rows)
    # Расчёт целевого прямоугольника независимо от временных адресов SP в коде.
    wanted=[pixel_address(144+8*row+scan,20)+column
        for row in range(6) for scan in range(6) for column in range(12)]
    assert Counter(prepared['screen_write_addresses'])==Counter(wanted)
    for view in (initial,prepared):
        assert len(view['screen_write_addresses'])==432
        assert all(0x4000<=a<0x5800 for a in view['screen_write_addresses'])
        assert view['code_write_addresses']==[SAVED,SAVED+1]
        assert not ({0xDB01,0xDB02}&set(view['screen_write_addresses']+view['code_write_addresses']))
    # Контроль изменённого операнда должен показать реальное пересечение наблюдаемой длины.
    altered=list(initialized);altered[0xED37:0xED39]=[3,0xDB]
    dangerous=analyze(altered,rows)
    assert {0xDB01,0xDB02}<=set(dangerous['screen_write_addresses'])
    rejected=0
    for pc,opcode in ((0xED2C,0xF9),(0xED3A,0x77)):
        altered=list(initialized);altered[pc]=opcode
        try:
            analyze(altered,rows)
        except AssertionError:
            rejected+=1
        else:
            raise AssertionError(('unknown_pointer_or_writer_accepted',hex(pc)))
    result=dict(passed=True,original_disk_sha256=manifest['sha256'],entry=START,end_exclusive=END,
        original_code_bytes=END-START,original_code_sha256=sha256(bytes(original[START:END])).hexdigest(),
        prepared_code_sha256=sha256(bytes(initialized[START:END])).hexdigest(),registered_instructions=len(rows),
        raw_view_unique_screen_bytes=len(set(initial['screen_write_addresses'])),
        prepared_unique_screen_bytes=len(set(prepared['screen_write_addresses'])),screen_write_count=432,
        screen_physical_bank=5,screen_write_addresses=sorted(set(prepared['screen_write_addresses'])),
        code_write_addresses=[SAVED,SAVED+1],code_physical_bank=1,push_instructions=216,pop_instructions=180,
        LD_SP_immediates=67,input_SP_and_pixel_values_do_not_change_write_addresses=True,
        saved_input_SP_restored_before_RET=True,own_writes_disjoint_from_bank1_DB01_DB02=True,
        altered_destination_reaches_DB01_DB02=True,unknown_pointer_or_store_controls_rejected=rejected,
        prepared_initializer_executed_and_independent_reference_matched=True,
        initialized_operands_and_unmodified_opcodes_required=True,
        all_callers_and_runtime_modifications_proved=False,IRQ_or_other_region_writes_excluded=False,
        scroll_execution_model_run=False,native_execution=False,assembly_executed=False)
    path=ROOT/'Tools/Disasm/Reports/ControlsScrollStoreBoundsVerification.json'
    if path.exists():
        assert json.loads(path.read_bytes())==result
    else:
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='screen_write_addresses'},ensure_ascii=False))


if __name__=='__main__':
    main()
