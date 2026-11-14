"""Расхождения опубликованных заголовков и действующего реестра, без изменения исходников."""
from collections import Counter,defaultdict
import json
import re
import sys

from CheckIntro import ROOT
from Contracts import CONTRACTS


def header(path):
    sections={}
    part=None
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        # Основной договор заканчивается до первого исполняемого кода, внутренние входы имеют свои заголовки.
        if sections and line.strip() and not line.lstrip().startswith(';'):
            break
        match=re.fullmatch(r'\s*;\s*(In|Out|Corrupt|Note):\s*',line)
        if match:
            part=match[1]
            sections.setdefault(part,[])
            continue
        if part:
            if re.fullmatch(r'\s*;\s*-+\s*',line):
                part=None
                continue
            if line.strip() and not line.lstrip().startswith(';'):
                break
            match=re.match(r'\s*;   (.*)',line)
            if match:
                sections[part].append(match[1])
    return sections


def inspect():
    functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_bytes())
    by_path=defaultdict(list)
    for function in functions:
        by_path[function['path']].append(function)
    counts=Counter()
    missing=[]
    differences=[]
    ambiguous=[]
    providers=defaultdict(list)
    research=(ROOT/'Tools/Disasm/Research').resolve()
    # Сведения берутся только из уже загруженных реестром модулей, сторонние сценарии не импортируются.
    for name,module in list(sys.modules.items()):
        if name in ('Contracts',__name__):
            continue
        path=getattr(module,'__file__',None)
        if not path or not research.joinpath(name+'.py').is_file():
            continue
        if not str(path).replace('\\','/').endswith('/'+name+'.py'):
            continue
        values=vars(module).get('CONTRACTS')
        if not isinstance(values,dict):
            continue
        for key,value in values.items():
            providers[key].append((name,value))
    for path,rows in by_path.items():
        # Проверка только однозначно связанного заголовка, общие файлы не сопоставляются наугад.
        if len(rows)!=1:
            ambiguous.append(dict(path=path,functions=len(rows)))
            continue
        function=rows[0]
        sections=header(ROOT/path)
        if not all(key in sections for key in ('In','Out','Corrupt')):
            counts['header_not_parsed']+=1
            continue
        contract=CONTRACTS.get((function['region'],function['address']))
        identity=dict(path=path,region=function['region'],address=function['address'])
        if contract is None:
            missing.append(identity)
            continue
        changed=[]
        for index,key in enumerate(('In','Out','Corrupt','Note')):
            current=sections.get(key,[])
            if current!=contract[index]:
                changed.append(dict(section=key,source=current,registry=contract[index]))
        if changed:
            # Повторы учитываются, совпадение множеств не должно скрывать потерянное примечание.
            same_statements=all(Counter(row['source'])==Counter(row['registry']) for row in changed)
            if same_statements:
                kind='note_order_only' if all(row['section']=='Note' for row in changed) else 'other_statement_order_only'
            else:
                kind='statement_content_difference'
            counts[kind]+=1
            published=[sections.get(key,[]) for key in ('In','Out','Corrupt','Note')]
            differences.append(dict(**identity,differences=changed,difference_kind=kind,
                matching_source_contract_modules=sorted(name for name,value in providers[function['region'],function['address']]
                                                        if list(value)==published),
                matching_current_contract_modules=sorted(name for name,value in providers[function['region'],function['address']]
                                                         if value==contract)))
        else:
            counts['exact_match']+=1
    return dict(method='read_only_header_registry_comparison_single_function_files',
        counts=dict(counts),missing=missing,different=differences,multiple_function_files=ambiguous,
        exact_order_comparison_preserved=True,statement_permutation_is_not_semantic_proof=True,
        source_modified=False,assembly_executed=False)


def main():
    result=inspect()
    (ROOT/'Tools/Disasm/Reports/ContractRegistryDriftInspection.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(**result['counts'],missing=len(result['missing']),
        different=len(result['different']),multiple_function_files=len(result['multiple_function_files']))))


if __name__=='__main__':
    main()
