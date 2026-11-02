"""Разделение чтения слова и самостоятельного входа применения параметров после RET AC43."""
import contextlib
import hashlib
import io
import json
import re
import sys
from ClassifyControlsTextDisplay import ROOT
from VerifySources import main as verify
from CheckControlsTextQueue import base_memory
from SourcePresentation import instructions


def main():
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):
        return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    proof = read('ActionParameterActivationVerification')
    assert proof['passed'] and proof['real_out_and_physical_eight_banks'] and proof['exact_registers_flags_r_and_sp']
    functions,source_map,symbols,flow,modified,inventory = (read(n) for n in ('Functions','SourceMap','Symbols','ControlFlow','ModifiedCode','Inventory'))
    region = next(r for r in flow if r['name']=='Action')
    candidate = ROOT/'Tools/Disasm/Research/Candidates/ActionParameterEntrySplit'
    history = ROOT/'Tools/Disasm/Research/History/BeforeActionParameterEntrySplit'
    assert not candidate.exists() and not history.exists()
    pending,renames = {},{}
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    # Разделение только после исходных RET, новых инструкций и адресов не создаётся.
    for entry,boundary in ((0xAC38,0xAC44),):
        f = next(f for f in functions if f['region']=='Action' and f['address']==entry)
        assert f['semantic_status']=='unknown'
        old_name,new_name = f['name'],'Unknown'+format(boundary,'04X')
        new = dict(f,name=new_name,address=boundary,offset=boundary-0x6000,path='Source/Action/'+new_name+'.asm')
        old_end = f['end_offset']
        f['end_offset'] = boundary-0x6000
        functions.insert(functions.index(f)+1,new)
        path = ROOT/f['path']
        lines = path.read_text('utf-8').splitlines()
        index = next(i for i,line in enumerate(lines) if line == '                LD A, #10')
        head = '\n'.join(lines[:index]).rstrip()+'\n\n                endmodule\n                endmodule\n'
        assert instructions(head)[-1]=='RET'
        head = head.replace('..#'+format(old_end-1,'04X'),'..#'+format(f['end_offset']-1,'04X'))
        entry_index = next(i for i,line in enumerate(lines) if line.startswith('Entry:'))
        header = lines[:entry_index]
        tail = header+lines[index:]
        tail = '\n'.join(tail)+'\n'
        tail = tail.replace('module '+old_name,'module '+new_name,1)
        tail = tail.replace(lines[index], 'Entry:'.ljust(16)+lines[index][16:], 1)
        tail = tail.replace('#'+format(entry-0x6000,'04X')+'..','#'+format(boundary-0x6000,'04X')+'..',1)
        assert instructions(head)+instructions(tail)==instructions(path.read_text('utf-8'))
        pending[path],pending[ROOT/new['path']] = head.encode('utf-8'),tail.encode('utf-8')
        for key,address in list(symbols.items()):
            if key.startswith('Action.'+old_name+'.') and boundary<=address<0x6000+old_end:
                last = 'Entry' if address==boundary else key.rsplit('.',1)[1]
                replacement = 'Action.'+new_name+'.'+last
                assert replacement not in symbols
                renames[key] = replacement
                symbols[replacement] = symbols.pop(key)
        # Вход AC44 доказан переходом из банка 1, прежней внутренней метки не было.
        assert 'Action.UnknownAC44.Entry' not in symbols
        controls = next(r for r in flow if r['name']=='Controls')
        assert next(i for i in controls['instructions'] if i['address']==0xDE0D)['operation']=='JP #AC44'
        symbols['Action.UnknownAC44.Entry'] = 0xAC44
        item = next(i for i in source_map if i['path']==f['path'])
        item['length'] = f['end_offset']-f['offset']
        item['sha256'] = hashlib.sha256(source[f['offset']:f['end_offset']]).hexdigest()
        source_map.insert(source_map.index(item)+1,dict(slot=17,offset=new['offset'],length=old_end-new['offset'],
            kind='code',path=new['path'],origin=boundary,sha256=hashlib.sha256(source[new['offset']:old_end]).hexdigest()))
        for item in modified:
            if item['region']=='Action' and boundary<=item['writer']<0x6000+old_end:
                assert item['path']==f['path']
                item['path']=new['path']
        region['roots'] = sorted(set(region['roots'])|{boundary})
        path = ROOT/'Source/Files/17_ACTION.inc'
        text = pending.get(path,path.read_bytes()).decode('utf-8')
        needle = '                include "../Action/'+old_name+'.asm"\n                ent'
        assert text.count(needle)==1
        replacement = (needle+'\n                assert $ == #'+format(boundary-0x6000,'04X')+'\n'
            '                disp #'+format(boundary,'04X')+'\n                include "../Action/'+new_name+'.asm"\n                ent')
        pending[path] = text.replace(needle,replacement).encode('utf-8')
        path = ROOT/'Docs/Functions.md'
        text = pending.get(path,path.read_bytes()).decode('utf-8')
        needle = next(line for line in text.splitlines() if line.startswith('| #'+format(entry,'04X')+' | [Action.'))
        row = '| #'+format(boundary,'04X')+' | [Action.'+new_name+'](../'+new['path']+') | Unknown, назначение этого фрагмента ещё не установлено |'
        pending[path] = text.replace(needle,needle+'\n'+row).encode('utf-8')
        path = ROOT/'Docs/FunctionDetails/Action.md'
        text = pending.get(path,path.read_bytes()).decode('utf-8')
        start = text.index('## '+old_name+'\n')
        end = text.find('\n## ',start+4)
        end = len(text) if end<0 else end
        blocks = []
        for fn in (f,new):
            blocks.append('## '+fn['name']+'\n\n[Action.'+fn['name']+'](../../'+fn['path']+')\n\n'
                'Unknown, назначение этого фрагмента ещё не установлено.\n\nВход `#'+format(fn['address'],'04X')+'`, запись 22, смещения `#'+format(fn['offset'],'04X')+'..#'+format(fn['end_offset']-1,'04X')+'`.\n\n')
        pending[path] = (text[:start]+''.join(blocks)+text[end:]).encode('utf-8')
    # Обновление только ссылок на перенесённые внутренние метки.
    for folder,pattern in (('Source','*.asm'),('Docs','*.md')):
        for path in (ROOT/folder).rglob(pattern):
            text = pending.get(path,path.read_bytes()).decode('utf-8')
            changed = text
            for before,after in renames.items():
                changed = re.sub(r'\b'+re.escape(before)+r'\b',after,changed)
            if changed!=text:
                lines=[]
                for line in changed.splitlines():
                    code,sep,note=line.partition(';')
                    lines.append(code.rstrip().ljust(80)+';'+note if sep and code.strip() else line)
                pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    # Новые файлы ещё отсутствуют при rglob, их ссылки обрабатываются отдельно.
    for path,data in list(pending.items()):
        if path.suffix=='.asm':
            text=data.decode('utf-8')
            for before,after in renames.items():
                text=re.sub(r'\b'+re.escape(before)+r'\b',after,text)
            pending[path]=text.encode('utf-8')
    inventory.update(fragments=len(functions),unknown=sum(f['semantic_status']!='described' for f in functions))
    inventory['ranges_by_kind']['code'] += 1
    for name,value in (('Functions',functions),('SourceMap',source_map),('Symbols',symbols),('ControlFlow',flow),('ModifiedCode',modified),('Inventory',inventory)):
        pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')] = encode(value)
    path = ROOT/'Docs/Functions.md'
    text = pending[path].decode('utf-8')
    total = sum(f['region']=='Action' for f in functions)
    text,count = re.subn(r'\| Action \| \d+ \|', '| Action | '+str(total)+' |',text,count=1)
    assert count==1
    pending[path] = text.encode('utf-8')
    path = ROOT/'Tools/Disasm/Research/Knowledge.py'
    text = path.read_text('utf-8')
    text += "\n# Самостоятельный вход AC44 после RET AC43, проверены реальные OUT и страницы.\nFUNCTIONS['Action'].update({0xAC44: ('UnknownAC44', 'Unknown, назначение этого фрагмента ещё не установлено')})\n"
    pending[path] = text.encode('utf-8')
    plan = [(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
    for path,before,after in plan:
        assert path.read_bytes()==before if before is not None else not path.exists()
        if before is not None:
            target=history/path.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(before)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    result = dict(passed=True,split_after_original_ret='AC43',additional_physical_fragments=1,
        instruction_sequence_preserved=True,physical_bytes_preserved=True,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionParameterEntrySplitClassification.json').write_bytes(encode(result))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
