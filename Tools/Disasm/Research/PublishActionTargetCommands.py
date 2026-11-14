"""Публикация проверенных команд из исходной таблицы клавиш через отдельный кандидат."""
from collections import Counter
import argparse,contextlib,hashlib,importlib,io,json,re,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
import VerifySources
from InspectZ80 import decoder
from CheckActionParameterActivation import flat_action
from SourcePresentation import format_function
from ValidateNotes import validate_notes


def main():
    parser=argparse.ArgumentParser();parser.add_argument('facts',nargs='?',default='ActionTargetCommandsFacts',choices=('ActionTargetCommandsFacts','ActionOverlayModeCommandFacts','ActionTractorModeCommandFacts','ActionFreeFlightCommandFacts','ActionStationReturnCommandFacts','ActionEjectCommandsFacts','ActionReverseViewBasisFacts','ActionViewDirectionCommandFacts','ActionTractorCollectFacts','ActionAntimissileCommandFacts','ActionBoostCommandFacts','ActionBoostAdvanceFacts','ActionHyperJumpFacts','ActionHyperJumpPreparationFacts','ActionHyperReloadFacts','ControlsDirectStationRelayFacts','ControlsStateStationRelayFacts','ControlsResetFlightContextFacts','ControlsLegacyLoadChainFacts','SecondaryEquipmentRowsFacts','ControlsBodyPrimaryMaskFacts','DrawCenteredWithoutOwnerFacts','ArcHalfLimitInputsFacts','IntroDetachedTailFacts','IntroAttributeCountTailFacts','IntroDetachedUnpackGateFacts','IntroAttributeScanPrefixFacts','StationAllFilledBandFacts','ActionRandomClassGateEntryFacts','ControlsEvenSpanPrefixFacts'));args=parser.parse_args()
    facts=importlib.import_module(args.facts);tag=facts.TAG;alias=tag.upper();module=args.facts
    document=getattr(facts,'DOCUMENT',tag)
    slot=getattr(facts,'SLOT',17);region_name=getattr(facts,'REGION','Action');assert slot in (3,4,7,17,22,23)
    if slot!=17:assert not facts.KEYS
    disk_name={3:'AWAKEN',4:'STATIONF',7:'KARTA',17:'ACTION',22:'CONTROL0',23:'CONTROL'}[slot]
    reports=ROOT/'Tools/Disasm/Reports'
    def read(name):return json.loads((reports/(name+'.json')).read_bytes())
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    proof=read(getattr(facts,'PROOF',tag+'Verification'))
    proof_cases=facts.proof_cases(proof) if hasattr(facts,'proof_cases') else proof.get('total_cases',proof.get('cases'))
    assert proof['passed'] and proof_cases==facts.CASES
    sm,symbols,inventory,functions,flow,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','Functions','ControlFlow','ModifiedCode')]
    suffix = '.B.sectors.bin' if slot == 3 else '.C.bin'
    raw=(ROOT/('Tools/Disasm/Extracted/Active/'+format(slot,'02d')+'_'+disk_name+suffix)).read_bytes();start,end=min(facts.FUNCTIONS),max(facts.ENDS.values())
    def file_offset(address):
        if hasattr(facts,'file_offset'):return facts.file_offset(address)
        return address-0x6000+(0x23D if 0x6000<=address<0x7F8F else 0)
    first=file_offset(start);last=first+end-start
    old=next(r for r in sm if r['slot']==slot and r['offset']<=first<last<=r['offset']+r['length'])
    assert old['kind']=='unclassified';old_path=ROOT/old['path'];assert old_path.read_bytes()==raw[old['offset']:old['offset']+old['length']]
    flat=flat_action()
    if hasattr(facts,'file_offset'):flat[start:end]=raw[first:last]
    decoded=decoder(flat).disassemble(start,end,'h')
    records=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex(),slot=slot,offset=file_offset(i.address)) for i in decoded]
    assert b''.join(bytes.fromhex(i['hex']) for i in records)==raw[first:last]
    region=next(r for r in flow if r['name']==region_name)
    assert not any(start<=i['address']<end for i in region['instructions'])
    region['instructions']=sorted(region['instructions']+records,key=lambda i:(i['slot'],i['offset']))
    region['roots']=sorted(set(region['roots'])|set(facts.FUNCTIONS))
    for field,pattern in (('calls',r'^CALL (?:[A-Z]+,)?#([0-9A-F]{4})$'),('branches',r'^(?:JP|JR) (?:[A-Z]+,)?#([0-9A-F]{4})$')):
        region[field]=sorted(set(region[field])|{int(match[1],16) for i in records if (match:=re.fullmatch(pattern,i['operation']))})
    region['instruction_count']+=len(records);region['code_bytes']+=end-start;region['classified_fraction']=region['code_bytes']/region['total_bytes']
    validate_notes([region],{region_name:facts.COMMENTS});pending={};pieces=[];new_functions=[]
    def unknown(begin,finish):
        if begin==finish:return
        path='Source/Resources/'+format(slot,'02d')+'_'+disk_name+'/Unclassified'+format(begin,'04X')+'_'+format(finish,'04X')+'.bin'
        assert not (ROOT/path).exists();pending[ROOT/path]=raw[begin:finish]
        pieces.append(dict(slot=slot,offset=begin,length=finish-begin,kind='unclassified',path=path,origin=None,sha256=hashlib.sha256(raw[begin:finish]).hexdigest()))
    unknown(old['offset'],first)
    for address,(name,description) in facts.FUNCTIONS.items():
        stop=facts.ENDS[address];offset=file_offset(address);stop_offset=offset+stop-address
        path='Source/'+region_name+'/'+name+'.asm';assert not (ROOT/path).exists()
        function=dict(region=region_name,name=name,address=address,slot=slot,offset=offset,end_offset=stop_offset,
            description=description,semantic_status='described',path=path)
        new_functions.append(function)
        pieces.append(dict(slot=slot,offset=offset,length=stop-address,kind='code',path=path,origin=address,sha256=hashlib.sha256(raw[offset:stop_offset]).hexdigest()))
        labels={address:'Entry',**{a:n for a,n in facts.LOCAL.items() if address<=a<stop}}
        for a,label in labels.items():
            key=region_name+'.'+name+'.'+label;assert key not in symbols;symbols[key]=a
        lines=['                module '+region_name,'                module '+name,
            '                ; Документация ['+facts.TITLE+'](../../Docs/'+document+'.md)',
            '                ; -----------------------------------------','                ; '+description,
            '                ; исходная запись '+str(slot)+', '+getattr(facts,'LOCATION','перенесённое ядро банка 5')+', адреса '+format(address,'04X')+'..'+format(stop-1,'04X')]
        for heading,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS[region_name,address]):
            lines+=['                ; '+heading+':']+['                ;   '+v for v in values]
        lines+=['                ; -----------------------------------------']
        for i in records:
            a=i['address']
            if not address<=a<stop:continue
            before,right=facts.COMMENTS.get(a,([],None));lines+=['                ; '+v for v in before]
            operation=facts.name_operands(region_name,address,i['operation'].replace(',',', '))
            line=((labels[a]+':').ljust(16) if a in labels else ' '*16)+operation
            if right:assert len(line)<80;line=line.ljust(80)+'; '+right
            lines.append(line)
        if address in getattr(facts,'CONTINUATIONS',{}):
            target=facts.CONTINUATIONS[address]
            name=(facts.FUNCTIONS[target][0] if target in facts.FUNCTIONS else
                  next(f['name'] for f in functions if f['region']==region_name and f['address']==target))
            lines.append('                ; JP @'+region_name+'.'+name+'.Entry, продолжение в '+name+'.asm')
        lines+=['                endmodule','                endmodule'];pending[ROOT/path]=format_function('\n'.join(lines)+'\n',None).encode('utf-8')
    unknown(last,old['offset']+old['length']);sm[sm.index(old):sm.index(old)+1]=pieces
    functions+=new_functions;functions.sort(key=lambda f:(f['region'],f['slot'],f['offset']))
    inventory.update(fragments=len(functions),described=sum(f['semantic_status']=='described' for f in functions),instructions=inventory['instructions']+len(records))
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm))
    inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==old['path']:
            row=next(r for r in pieces if r['offset']<=item['target_offset']<r['offset']+r['length'])
            item['target_path']=row['path'];item['target_source_classified']=row['kind']!='unclassified'
    for writer,target,size,instruction,target_path in facts.MUTATIONS:
        assert not any(i['region']==region_name and i['writer']==writer for i in modified)
        source_fn=next(f for f in new_functions if f['address']<=writer<f['address']+f['end_offset']-f['offset'])
        if target_path is None:
            target_offset=target-0x6000+(0x23D if target<0x7F8F else 0)
            row=next(r for r in sm if r['slot']==17 and r['offset']<=target_offset<r['offset']+r['length'])
            target_path=row['path']
        else:
            row=next(r for r in sm if r['path']==target_path);target_offset=row['offset']+target-row['origin']
        target_region_name=getattr(facts,'MUTATION_TARGET_REGION','Action')
        target_region=next(r for r in flow if r['name']==target_region_name)
        modified.append(dict(region=region_name,writer=writer,target=target,size=size,target_instruction=instruction,
            target_operation=next((i['operation'] for i in target_region['instructions'] if i['address']==instruction),'LD A,#00' if size==1 else 'LD HL,#0000'),path=source_fn['path'],target_path=target_path,
            target_region=target_region_name,target_slot=row['slot'],target_offset=target_offset))
    modified.sort(key=lambda r:(r['region'],r['writer'],r['target']))
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('Functions',functions),('ControlFlow',flow),('ModifiedCode',modified)):
        pending[reports/(stem+'.json')]=encode(value)
    p=ROOT/('Source/Files/'+format(slot,'02d')+'_'+disk_name+'.inc');text=p.read_text('utf-8');needle='                incbin "../Resources/'+format(slot,'02d')+'_'+disk_name+'/'+old_path.name+'"';assert text.count(needle)==1
    lines=[]
    for row in pieces:
        lines+=['                assert $ == #'+format(row['offset'],'04X')]
        if row['kind']=='code':
            continuation=getattr(facts,'CONTINUATIONS',{})
            position=0 if row['origin'] in continuation else 1 if row['origin'] in continuation.values() else None
            order='' if position is None else f' ; ({position}) жёсткий порядок, последовательное исполнение'
            lines+=['                disp #'+format(row['origin'],'04X'),'                include "../'+row['path'][7:]+'"'+order,'                ent']
        else:lines+=['                ; Unknown, соседний диапазон сохраняется без классификации','                incbin "../'+row['path'][7:]+'"']
    pending[p]=text.replace(needle,'\n'.join(lines)).encode('utf-8')
    p=ROOT/'Source/Action/Data/KeyHandlerPointers.asm';text=p.read_text('utf-8')
    for address in facts.KEYS:
        name,description=facts.FUNCTIONS[address]
        needle='#'+format(address,'04X');assert text.count(needle)==1
        text='\n'.join(('                    @Action.'+name+'.Entry').ljust(80)+'; Target, '+description[0].lower()+description[1:] if needle in line else line for line in text.splitlines())+'\n'
    if facts.KEYS:pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ActionKeyScanTables.py';text=p.read_text('utf-8')
    additions=''
    for address,index in facts.KEYS.items():
        name=facts.FUNCTIONS[address][0];target='@Action.'+name+'.Entry';assert target not in text
        additions+=f"    '{target}':('Index{index:02X}',0x{address:04X}),\n"
    if facts.KEYS:pending[p]=text.replace('NAMED_TARGETS={\n','NAMED_TARGETS={\n'+additions).encode('utf-8')
    for filename,field in (('Knowledge.py','FUNCTIONS'),('Contracts.py','CONTRACTS')):
        extra=f"\nfrom {module} import {field} as {alias}_{field}\n"
        extra+=(f"FUNCTIONS[{region_name!r}].update({alias}_FUNCTIONS)\n" if field=='FUNCTIONS' else f"CONTRACTS.update({alias}_CONTRACTS)\n")
        p=ROOT/'Tools/Disasm/Research'/filename;text=p.read_text('utf-8');assert 'from '+module not in text;pending[p]=(text+extra).encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=p.read_text('utf-8');needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    callback=tag.lower()+'_name_operands'
    text=text.replace(needle,needle+'\n    operation = '+callback+'(region,function_address,operation)')
    text+='\nfrom '+module+' import name_operands as '+callback+'\n'
    for address in facts.FUNCTIONS:text+=f"DOCUMENTS[{region_name!r},{address}]=('{document}','{facts.TITLE}')\n"
    for address,name in facts.LOCAL.items():text+=f"LABELS[{region_name!r},{address}]='{name}'\n"
    pending[p]=text.encode('utf-8')
    p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='\n\nif __name__ == "__main__":';assert text.count(needle)==1
    extra=f"\nfrom {module} import COMMENTS as {alias}_COMMENTS\nREGION_COMMENTS.setdefault({region_name!r},{{}}).update({alias}_COMMENTS)\n"
    pending[p]=text.replace(needle,extra+needle).encode('utf-8')
    if hasattr(facts,'prepare'):facts.prepare(pending,symbols,ROOT)
    pending[reports/'Symbols.json']=encode(symbols)
    p=ROOT/'Docs/Functions.md';text=p.read_text('utf-8');total=sum(f['region']==region_name for f in functions);described=sum(f['region']==region_name and f['semantic_status']=='described' for f in functions)
    text=re.sub(r'\| '+region_name+r' \| \d+ \| \d+ \|',f'| {region_name} | {total} | {described} |',text)
    rows=''.join('| #'+format(f['address'],'04X')+' | ['+region_name+'.'+f['name']+'](../'+f['path']+') | '+f['description']+' |\n' for f in new_functions)
    next_fn=min((f for f in functions if f['region']==region_name and f['address']>=end),key=lambda f:f['address'],default=None)
    if next_fn is None:
        previous=max((f for f in functions if f['region']==region_name and f['address']<start),key=lambda f:f['address'])
        needle=next(line for line in text.splitlines(keepends=True) if f"[{region_name}.{previous['name']}]" in line)
        pending[p]=text.replace(needle,needle+rows).encode('utf-8')
    else:
        needle='| #'+format(next_fn['address'],'04X')+' | ['+region_name+'.'+next_fn['name']+']';assert text.count(needle)==1
        pending[p]=text.replace(needle,rows+needle).encode('utf-8')
    p=ROOT/('Docs/FunctionDetails/'+region_name+'.md');text=p.read_text('utf-8')
    sections=''.join('## '+f['name']+'\n\n['+region_name+'.'+f['name']+'](../../'+f['path']+')\n\n'+f['description']+'.\n\n[Договоры и границы проверки](../'+document+'.md).\n\n' for f in new_functions)
    if next_fn is None:
        pending[p]=(text.rstrip()+'\n\n'+sections.rstrip()+'\n').encode('utf-8')
    else:
        needle='## '+next_fn['name']+'\n';assert text.count(needle)==1
        pending[p]=text.replace(needle,sections+needle).encode('utf-8')
    candidate=ROOT/('Tools/Disasm/Research/Candidates/'+tag);history=ROOT/('Tools/Disasm/Research/History/Before'+tag);assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    # Сохранение отдельного кандидата и исходного состояния перед точечной заменой.
    for p,before,after in plan:
        target=candidate/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before in {**{p:b for p,b,_ in plan if b is not None},old_path:old_path.read_bytes()}.items():
        target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    # Загрузка действующих проверок после точечного обновления исходников и реестров.
    importlib.reload(importlib.import_module('ActionKeyScanTables'))
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
    assert old_path.resolve().is_relative_to((ROOT/('Source/Resources/'+format(slot,'02d')+'_'+disk_name)).resolve())
    assert old_path.read_bytes()==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,functions=len(new_functions),code_bytes=end-start,instructions=len(records),model_cases=facts.CASES,
        original_bytes_and_addresses_preserved=True,assembly_executed=False,native_execution=False)
    (reports/(tag+'Classification.json')).write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
