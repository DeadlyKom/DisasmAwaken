"""Точечная разметка семи потоков, 21 байта состояний и отдельного входа очистки."""
from pathlib import Path
from collections import Counter
import contextlib
import io
import json
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from CandidateWorkspace import create_candidate
import VerifySources
import AuditConformance
import CheckDocumentation


def inside(record):return record['slot']==4 and 0x487B<=record['offset']<0x491B
def load(root,name):return json.loads((root/'Tools/Disasm/Reports'/name).read_text('utf-8'))
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def main():
    candidate=ROOT/'Tools/Disasm/Research/Candidates/RandomStateRelease'
    history=ROOT/'Tools/Disasm/Research/History/BeforeRandomStateRelease';assert not history.exists()
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    old_functions,new_functions=load(ROOT,'Functions.json'),load(candidate,'Functions.json')
    old_local=[f for f in old_functions if inside(f)];fresh_functions=[f for f in new_functions if inside(f)]
    assert len(old_local)==2 and len(fresh_functions)==9
    assert [f for f in old_functions if not inside(f)]==[f for f in new_functions if not inside(f)]
    old_map,new_map=load(ROOT,'SourceMap.json'),load(candidate,'SourceMap.json')
    old=[r for r in old_map if inside(r)];fresh=[r for r in new_map if inside(r)]
    assert len(old)==3 and len(fresh)==10
    assert sum(r['length'] for r in fresh if r['kind']=='typed_data')==21
    for record in fresh:assert 0x487B<=record['offset'] and record['offset']+record['length']<=0x491B
    pending={r['path']:(candidate/r['path']).read_bytes() for r in fresh}
    deletions={r['path'] for r in old}-{r['path'] for r in fresh}
    merged_map=sorted([r for r in old_map if not inside(r)]+fresh,key=lambda r:(r['slot'],r['offset']))
    old_flow,new_flow=load(ROOT,'ControlFlow.json'),load(candidate,'ControlFlow.json')
    for before,after in zip(old_flow,new_flow):
        assert before['name']==after['name']
        assert [i for i in before['instructions'] if not inside(i)]==[i for i in after['instructions'] if not inside(i)]
    # Переименование старых символов выполняется по адресу, общий хвост становится отдельной процедурой.
    symbols=load(candidate,'Symbols.json');old_symbols=load(ROOT,'Symbols.json')
    prefixes=tuple('Station.'+f['name']+'.' for f in old_local)
    target_symbols={value:key for key,value in symbols.items()
                    if key.startswith(tuple('Station.'+f['name']+'.' for f in fresh_functions))}
    renames={key:target_symbols[value] for key,value in old_symbols.items() if key.startswith(prefixes)}
    path_map={f['path']:next(n['path'] for n in fresh_functions if n['offset']==f['offset']) for f in old_local}
    pattern=re.compile('|'.join(re.escape(key)+r'\b' for key in sorted(renames,key=len,reverse=True)))
    for folder in ('Source','Docs','Tools/Disasm/Reports'):
        for path in (ROOT/folder).rglob('*'):
            relative=path.relative_to(ROOT).as_posix()
            if not path.is_file() or relative in deletions or relative in pending or path.suffix not in ('.asm','.inc','.md','.json') or 'Runtime' in path.parts:continue
            before=path.read_text('utf-8');after=pattern.sub(lambda m:renames[m[0]],before)
            for old_path,new_path in path_map.items():
                after=after.replace(old_path,new_path).replace('../'+old_path[7:],'../'+new_path[7:])
            if before!=after:
                if path.suffix in ('.asm','.inc'):
                    lines=[]
                    for old_line,line in zip(before.splitlines(),after.splitlines()):
                        if old_line!=line and ';' in line and not line.lstrip().startswith(';'):
                            code,comment=line.split(';',1);assert len(code.rstrip())<80
                            line=code.rstrip().ljust(80)+';'+comment
                        lines.append(line)
                    after='\n'.join(lines)+'\n'
                pending[relative]=after.encode('utf-8')
    # Включения за пределами исходного участка сохраняются буквально.
    path='Source/Files/04_STATIONF.inc';text=(ROOT/path).read_text('utf-8');new_text=(candidate/path).read_text('utf-8')
    first,last='                assert $ == #487B\n','                assert $ == #491B\n'
    text=text[:text.index(first)]+new_text[new_text.index(first):new_text.index(last)]+text[text.index(last):]
    pending[path]=text.encode('utf-8')
    for name in ('Functions.json','ControlFlow.json','Symbols.json','ModifiedCode.json'):
        pending['Tools/Disasm/Reports/'+name]=(candidate/'Tools/Disasm/Reports'/name).read_bytes()
    pending['Tools/Disasm/Reports/SourceMap.json']=encoded(merged_map)
    inventory=load(ROOT,'Inventory.json');totals=Counter()
    for record in merged_map:totals[record['kind']]+=record['length']
    inventory.update(fragments=len(new_functions),described=sum(f['semantic_status']=='described' for f in new_functions),
                     unknown=sum(f['semantic_status']=='unknown' for f in new_functions),
                     instructions=sum(r['instruction_count'] for r in new_flow),physical_bytes_by_kind=dict(totals),
                     ranges_by_kind=dict(Counter(r['kind'] for r in merged_map)))
    pending['Tools/Disasm/Reports/Inventory.json']=encoded(inventory)
    pending['Docs/ModifiedCode.md']=(candidate/'Docs/ModifiedCode.md').read_bytes()
    # Раздел старого общего фрагмента заменяется точными разделами семи потоков, ядра и очистки.
    path='Docs/FunctionDetails/Station.md';text=(ROOT/path).read_text('utf-8');new_text=(candidate/path).read_text('utf-8')
    start='## '+old_local[0]['name']+'\n';end='## UnknownA91B\n'
    begin='## '+fresh_functions[0]['name']+'\n'
    text=text[:text.index(start)]+new_text[new_text.index(begin):new_text.index(end)]+text[text.index(end):]
    # Прочие разделы могут ссылаться на прежние имена процедур, адресная замена сохраняется и здесь.
    text=pattern.sub(lambda m:renames[m[0]],text)
    for old_path,new_path in path_map.items():text=text.replace(old_path,new_path)
    pending[path]=text.encode('utf-8')
    path='Docs/Functions.md';lines=(ROOT/path).read_text('utf-8').splitlines();new_lines=(candidate/path).read_text('utf-8').splitlines()
    selected=[i for i,line in enumerate(lines) if '| [Station.' in line]
    lines[selected[0]:selected[-1]+1]=[line for line in new_lines if '| [Station.' in line]
    lines=[next(n for n in new_lines if n.startswith('| Station |')) if line.startswith('| Station |') else line for line in lines]
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    review=create_candidate(ROOT,'Tools/Disasm/Research/Candidates/RandomStateMergeReview','documentation')
    for path,data in pending.items():
        target=review/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path in deletions:
        target=(review/path).resolve();assert target.is_relative_to(review/'Source');target.unlink()
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.ROOT=review;VerifySources.main()
    CheckDocumentation.ROOT=review;documents=CheckDocumentation.audit();assert documents['passed'],documents
    AuditConformance.ROOT=review;audit=AuditConformance.audit()
    for key in ('unlinked_functions','missing_includes_or_resources','missing_include_order','unresolved_global_references',
                'duplicate_global_definitions','global_reference_case_mismatches','source_files_outside_graph','python_duplicate_literal_keys'):
        assert not audit[key],(key,audit[key])
    # История сохраняет все заменяемые и архивируемые файлы перед записью в текущую рабочую копию.
    for path in set(pending)|deletions:
        original=ROOT/path
        if original.exists():
            backup=history/path;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,backup)
    for path,data in pending.items():
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path in deletions:
        target=(ROOT/path).resolve();assert target.is_relative_to(ROOT/'Source');target.unlink()
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.ROOT=ROOT;VerifySources.main()
    AuditConformance.ROOT=ROOT;audit=AuditConformance.audit()
    (ROOT/'Tools/Disasm/Reports/ConformanceAudit.json').write_bytes(encoded(audit))
    CheckDocumentation.ROOT=ROOT;documents=CheckDocumentation.audit();assert documents['passed']
    (ROOT/'Tools/Disasm/Reports/DocumentationVerification.json').write_bytes(encoded(documents))
    report=dict(passed=True,method='scoped_random_state_merge_after_independent_candidate_validation',
                old_fragments=2,new_fragments=9,physical_state_records=7,new_typed_bytes=21,new_code_bytes=42,new_instructions=18,
                instruction_count=inventory['instructions'],remaining_unknown=audit['unknown_fragments'],
                remaining_contracts=audit['unknown_contract_fragments'],assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RandomStateReleaseVerification.json').write_bytes(encoded(report))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
