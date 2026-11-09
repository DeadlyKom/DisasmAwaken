"""Именование только доказанных LD DE,строка перед CALL банковой очереди, без изменения байтов."""
import contextlib,io,json,re,sys
from CheckIntro import ROOT
from CheckControlsTextQueue import payload
import ControlsFlightMessages as facts
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    names={r['address']:r['name'] for r in facts.records(payload(23))};functions=read('Functions');instructions=next(r for r in read('ControlFlow') if r['name']=='Action')['instructions']
    allowed={};sites=[]
    # Проверка непосредственного CALL 6040 после каждого кандидата LD DE, это не только числовое совпадение.
    for index,item in enumerate(instructions):
        match=re.fullmatch(r'LD DE,#([0-9A-F]{4})',item['operation'])
        if not match or int(match[1],16) not in names:continue
        following=instructions[index+1];assert following['address']==item['address']+3 and following['operation']=='CALL #6040'
        owner=next(f for f in functions if f['region']=='Action' and f['slot']==item['slot'] and f['offset']<=item['offset']<f['end_offset'])
        address=int(match[1],16);allowed.setdefault(('Action',owner['address']),{})[address]=names[address]
        sites.append(dict(writer=item['address'],message_address=address,message_name=names[address],path=owner['path']))
    assert len(sites)==33
    module='ActionFlightMessageNames';helper='"""Адреса строк только из доказанных непосредственных вызовов банковой очереди."""\nCALL_FIELDS='+repr(allowed)+'\n\n'
    helper+='def name_operands(region,function_address,operation):\n    for address,name in CALL_FIELDS.get((region,function_address),{}).items():\n        operation=operation.replace("LD DE, #"+format(address,"04X"),"LD DE, @ControlsFlightText."+name)\n    return operation\n'
    pending={ROOT/('Tools/Disasm/Research/'+module+'.py'):helper.encode('utf-8')};changed=0
    for relative in sorted(set(s['path'] for s in sites)):
        path=ROOT/relative;before=path.read_text('utf-8');root=next(f['address'] for f in functions if f['path']==relative);fields=allowed['Action',root]
        lines=[];local=0
        for line in before.splitlines():
            match=re.search(r'LD DE, #([0-9A-F]{4})',line)
            if match and int(match[1],16) in fields:
                code,separator,comment=line.partition(';');operation='LD DE, @ControlsFlightText.'+fields[int(match[1],16)]
                code=code[:match.start()]+operation
                line=code.rstrip().ljust(80)+';'+comment if separator else code.rstrip();local+=1
            lines.append(line)
        if local:pending[path]=('\n'.join(lines)+'\n').encode('utf-8');changed+=local
    assert changed==23,changed
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8');needle='def name_operands(region, function_address, operation):';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = flight_message_name_operands(region,function_address,operation)')
    text+='\nfrom '+module+' import name_operands as flight_message_name_operands\n';pending[path]=text.encode('utf-8')
    path=ROOT/'Docs/ControlsFlightMessages.md';text=path.read_text('utf-8');text+='\n[Реестр обращений](../Tools/Disasm/Reports/ActionFlightMessageNamesVerification.json) подтверждает 33 непосредственных загрузки DE перед CALL 6040 из ACTION. У 23 ещё числовых обращений исходники используют имена ControlsFlightText, десять ранее именованных обращений сохраняют уже существующие смысловые константы. [Правила экспорта имён](../Tools/Disasm/Research/ActionFlightMessageNames.py) применяются только к этим доказанным функциям и значениям.\n';pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionFlightMessageNames';history=ROOT/'Tools/Disasm/Research/History/BeforeActionFlightMessageNames';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before,after in plan:
        if before is not None:
            q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,immediate_queue_calls=33,numeric_operands_named=changed,sites=sites,only_proved_call_6040_operands_changed=True,
        instructions_and_all_resource_bytes_preserved=True,assembly_executed=False,native_execution=False)
    (reports/'ActionFlightMessageNamesVerification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in result.items() if k!='sites'},indent=2))


if __name__=='__main__':main()
