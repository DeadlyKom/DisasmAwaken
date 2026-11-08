"""Типизация 45 соседних кодов по проверенной раскладке встроенного документа, без предположения обо всех потребителях."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionEquipmentData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    evidence=read('ActionEquipmentNotesMapping');assert evidence['passed'] and evidence['matched_bytes']==49
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    assert bytes(r['value'] for r in evidence['rows'])==source[0x3C10:0x3C41]
    sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    old=next(p for p in sm if p['slot']==17 and p['offset']==0x3C14)
    assert old['kind']=='unclassified' and old['length']==312
    old_path=ROOT/old['path'];old_end=old['offset']+old['length'];assert old_path.read_bytes()==source[0x3C14:old_end]
    pending={};pieces=[];new_symbols=0
    for table in facts.TABLES:
        module,path,start,end,_,_,names=table;assert all(len(n)<=15 for n in names)
        text,labels=facts.render(source,table);assert facts.parse(text,table)==(source[start:end],labels)
        assert not (ROOT/path).exists() and not set(labels)&set(symbols)
        symbols.update(labels);new_symbols+=len(labels);pending[ROOT/path]=text.encode('utf-8')
        pieces.append(dict(slot=17,offset=start,length=end-start,kind='typed_data',path=path,origin=start+0x6000,
            sha256=hashlib.sha256(source[start:end]).hexdigest()))
    suffix=f'Source/Resources/17_ACTION/Unclassified3C41_{old_end:04X}.bin';assert not (ROOT/suffix).exists()
    pending[ROOT/suffix]=source[0x3C41:old_end]
    pieces.append(dict(slot=17,offset=0x3C41,length=old_end-0x3C41,kind='unclassified',path=suffix,origin=None,
        sha256=hashlib.sha256(source[0x3C41:old_end]).hexdigest()))
    sm[sm.index(old):sm.index(old)+1]=pieces
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm))
    inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==str(old_path.relative_to(ROOT)).replace('\\','/'):
            assert item['target_slot']==17
            owner=next(p for p in pieces if p['offset']<=item['target_offset']<p['offset']+p['length'])
            item.update(target_path=owner['path'],target_source_classified=owner['kind']=='typed_data')
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for piece in pieces:
        lines+=['                assert $ == #'+format(piece['offset'],'04X')]
        if piece['kind']=='typed_data':
            lines+=['                disp #'+format(piece['origin'],'04X'),
                    '                include "../Action/Data/'+piece['path'].rsplit('/',1)[-1]+'"','                ent']
        else:lines+=['                ; Unknown, соседние байты вне подтверждённой раскладки оборудования',
                     '                incbin "../'+piece['path'][7:]+'"']
    pending[path]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FEquipmentCode' not in text
    pending[path]=text.replace('                endif',facts.structure()+'\n                endif').encode('utf-8')
    named=0
    for relative in ('Source/Action/UpdateBodyMotion.asm','Source/Action/UpdateFrame.asm','Source/Action/CheckRecordEffectThreshold.asm'):
        path=ROOT/relative;before=path.read_text('utf-8');after=facts.name_operands('Action',None,before)
        named+=sum(before.count('(#'+format(byte,'04X')+')') for byte in (0x9C1A,0x9C1B,0x9C1C,0x9C1D,0x9C1E,0x9C29))
        assert after!=before;pending[path]=after.encode('utf-8')
    assert named==6
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_equipment_name_operands(region,function_address,operation)')
    pending[path]=(text+'\nfrom ActionEquipmentData import name_operands as action_equipment_name_operands\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка девяти физических слов базиса и их двух байтовых полей.';assert text.count(needle)==1
    hook='''    # Проверка кодов корабля и скиммера по всей физической раскладке исходного документа.
    from ActionEquipmentData import TABLES as EQUIPMENT_TABLES, parse as parse_equipment
    for table in EQUIPMENT_TABLES:
        raw,labels=parse_equipment((ROOT/table[1]).read_text('utf-8'),table)
        assert raw==sources[17][table[2]:table[3]]
        assert all(symbols.get(k.upper())==v for k,v in labels.items())
        rows=[p for p in source_map if p['path']==table[1]]
        assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(table[2],table[3]-table[2],table[2]+0x6000)
    assert symbols['FEQUIPMENTCODE']==1 and symbols['FEQUIPMENTCODE.VALUE']==0

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Раскладка кодов оборудования из того же исходного образа, имена не означают полный игровой разбор.
    from ActionEquipmentData import TABLES as EQUIPMENT_TABLES, render as render_equipment
    for table in EQUIPMENT_TABLES:
        equipment_text,equipment_labels=render_equipment(data_by_slot[17],table)
        write(table[1],equipment_text);symbols.update(equipment_labels)
        special[17,table[2]]=(table[3],table[1],table[2]+0x6000)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Docs/ActionEmbeddedNotes.md'
    pending[path]=(path.read_text('utf-8')+'\n[Раскладка оборудования](ActionEquipmentCodes.md) сопоставлена со всеми 49 исходными байтами. Подтверждены соответствия нескольким реальным потребителям, полный игровой смысл каждого элемента остаётся отдельным вопросом.\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionEquipmentData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionEquipmentData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/old_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_path.read_bytes())
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='equipment-data-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x3C14:old_end]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=45,physical_records=45,matched_author_layout_bytes=49,
        existing_four_fuel_missile_bytes_not_duplicated=True,new_physical_symbols=new_symbols,named_operand_sites=named,
        original_bytes_and_instructions_preserved=True,all_item_game_consumers_proved=False,
        skimmer_gameplay_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionEquipmentDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
