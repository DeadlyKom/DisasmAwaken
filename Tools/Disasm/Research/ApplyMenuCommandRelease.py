"""Точечное выделение трёх исходных участков команд меню из сырых байтов после отдельной проверки."""
from pathlib import Path
from collections import Counter
import contextlib
import io
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from CandidateWorkspace import create_candidate
import VerifySources
import AuditConformance
import CheckDocumentation

INTERVALS=((0x17E8,0x181F),(0x4770,0x47F5),(0x66B0,0x6873))


def inside(record):
    return record['slot']==4 and any(a<=record['offset']<b for a,b in INTERVALS)


def load(root,name):return json.loads((root/'Tools/Disasm/Reports'/name).read_text('utf-8'))
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')


def check_documents(root):
    CheckDocumentation.ROOT=root
    report=CheckDocumentation.audit()
    assert report['passed'],report
    (root/'Tools/Disasm/Reports/DocumentationVerification.json').write_bytes(encoded(report))


def main():
    candidate=ROOT/'Tools/Disasm/Research/Candidates/MenuCommandRelease'
    history=ROOT/'Tools/Disasm/Research/History/BeforeMenuCommandRelease'
    assert not history.exists()
    with contextlib.redirect_stdout(io.StringIO()):VerifySources.main()
    old_functions,new_functions=load(ROOT,'Functions.json'),load(candidate,'Functions.json')
    old_map,new_map=load(ROOT,'SourceMap.json'),load(candidate,'SourceMap.json')
    assert [f for f in old_functions if not inside(f)]==[f for f in new_functions if not inside(f)]
    fresh_functions=[f for f in new_functions if inside(f)]
    assert len(fresh_functions)==9 and not any(inside(f) for f in old_functions)
    fresh=[dict(r) for r in new_map if inside(r)]
    old=[r for r in old_map if inside(r)]
    assert len(old)==3 and all(r['kind']=='unclassified' for r in old)
    pending={};renames={}
    # Сохранение исходного имени сырого префикса, все прочие сырые байты находятся вне этапа.
    for record in fresh:
        assert any(a<=record['offset'] and record['offset']+record['length']<=b for a,b in INTERVALS)
        source_path=record['path']
        if record['kind']=='unclassified':
            previous=next(r for r in old if r['offset']==record['offset'])
            record['path']=previous['path'];renames[source_path]=record['path']
            assert (ROOT/previous['path']).read_bytes()[:record['length']]==(candidate/source_path).read_bytes()
        else:assert record['kind']=='code'
        pending[record['path']]=(candidate/source_path).read_bytes()
    deletions={r['path'] for r in old}-{r['path'] for r in fresh}
    merged_map=sorted([r for r in old_map if not inside(r)]+fresh,key=lambda r:(r['slot'],r['offset']))
    # Проверка потоков инструкций вне новых физических участков запрещает сопутствующий переразбор.
    old_flow,new_flow=load(ROOT,'ControlFlow.json'),load(candidate,'ControlFlow.json')
    assert [r['name'] for r in old_flow]==[r['name'] for r in new_flow]
    for before,after in zip(old_flow,new_flow):
        assert [i for i in before['instructions'] if not inside(i)]==[i for i in after['instructions'] if not inside(i)]
    path='Source/Files/04_STATIONF.inc'
    text=(ROOT/path).read_text('utf-8');new_text=(candidate/path).read_text('utf-8')
    for begin,end in INTERVALS:
        first,last=f'                assert $ == #{begin:04X}\n',f'                assert $ == #{end:04X}\n'
        chunk=new_text[new_text.index(first):new_text.index(last)]
        for before,after in renames.items():chunk=chunk.replace(before[7:],after[7:])
        text=text[:text.index(first)]+chunk+text[text.index(last):]
    # Продолжение после условного RET требует отметки и у уже существовавшего следующего файла.
    old_line='                include "../Station/DropItemDraw.asm"'
    ordered_line=next(line for line in new_text.splitlines() if line.startswith(old_line))
    text=text.replace(old_line+'\n',ordered_line+'\n')
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
    # Вставка новых разделов не заменяет существующие ручные пояснения документации.
    path='Docs/FunctionDetails/Station.md';text=(ROOT/path).read_text('utf-8');new_text=(candidate/path).read_text('utf-8')
    for function in fresh_functions:
        marker='## '+function['name']+'\n';begin=new_text.index(marker);end=new_text.find('\n## ',begin+len(marker))
        section=new_text[begin:end+1] if end>=0 else new_text[begin:]
        following=next(f for f in new_functions[new_functions.index(function)+1:] if f in old_functions and f['region']=='Station')
        anchor='## '+following['name']+'\n';text=text.replace(anchor,section+'\n'+anchor,1)
    pending[path]=text.encode('utf-8')
    path='Docs/Functions.md';lines=(ROOT/path).read_text('utf-8').splitlines();fresh_lines=(candidate/path).read_text('utf-8').splitlines()
    selected=[i for i,line in enumerate(lines) if '| [Station.' in line]
    lines[selected[0]:selected[-1]+1]=[line for line in fresh_lines if '| [Station.' in line]
    lines=[next(n for n in fresh_lines if n.startswith('| Station |')) if line.startswith('| Station |') else line for line in lines]
    pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    review=create_candidate(ROOT,'Tools/Disasm/Research/Candidates/MenuCommandMergeReview2','documentation')
    for path,data in pending.items():
        target=review/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path in deletions:
        target=(review/path).resolve();assert target.is_relative_to(review/'Source');target.unlink()
    with contextlib.redirect_stdout(io.StringIO()):
        VerifySources.ROOT=review;VerifySources.main()
        check_documents(review)
    AuditConformance.ROOT=review;audit=AuditConformance.audit()
    for key in ('unlinked_functions','missing_includes_or_resources','missing_include_order',
                'unresolved_global_references','duplicate_global_definitions','global_reference_case_mismatches',
                'source_files_outside_graph','python_duplicate_literal_keys'):assert not audit[key],(key,audit[key])
    # Архивирование каждого затрагиваемого файла предшествует записи в рабочую копию.
    for path in set(pending)|deletions:
        original=ROOT/path
        if original.exists():
            backup=history/path;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,backup)
    for path,data in pending.items():
        target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path in deletions:
        target=(ROOT/path).resolve();assert target.is_relative_to(ROOT/'Source');target.unlink()
    with contextlib.redirect_stdout(io.StringIO()):
        VerifySources.ROOT=ROOT;VerifySources.main()
        check_documents(ROOT)
    AuditConformance.ROOT=ROOT;audit=AuditConformance.audit()
    (ROOT/'Tools/Disasm/Reports/ConformanceAudit.json').write_bytes(encoded(audit))
    report=dict(passed=True,method='scoped_menu_command_merge_after_independent_candidate_validation',
                new_functions=9,new_code_bytes=209,new_instructions=99,archived_files=len(deletions),
                instruction_count=inventory['instructions'],unknown_fragments=audit['unknown_fragments'],
                unknown_contracts=audit['unknown_contract_fragments'],assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MenuCommandReleaseVerification.json').write_bytes(encoded(report))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
