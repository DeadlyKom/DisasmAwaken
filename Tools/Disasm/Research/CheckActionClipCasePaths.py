"""Сверка всех байтов ACTION-случаев с картой и всех абстрактных путей, без геометрической подмены."""
import inspect,json,re
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from InspectZ80 import decoder
import CheckClipCasePaths as paths
import DescribeClipDecisions as decisions


def translated(address):
    if 0xD4E5<=address<0xD9A9:return address-0x146B
    if 0xD9A9<=address<0xDA52:return address-0x146C
    if 0xDA52<=address<0xDAB0:return address-0x146E
    if 0xDAB0<=address<=0xDB59:return address-0x146F
    if address==0xDE39:return 0xCF07
    raise AssertionError(('неустановленное соответствие',hex(address)))


def adapted(function):
    namespace=dict(function.__globals__)
    for name in ('PRODUCT','APPEND','DIFFERENCE','CORNERS'):
        if name in namespace:namespace[name]={translated(a):v for a,v in namespace[name].items()}
    text=inspect.getsource(function)
    for old,new in ((0xDAB0,0xC641),(0xDABB,0xC64C),(0xDAC6,0xC657),(0xDAD1,0xC662),
        (0xDB2C,0xC6BD),(0xDB37,0xC6C8),(0xDB42,0xC6D3),(0xDB59,0xC6EA),(0xD4DD,0xC993),(0xDE39,0xCF07)):
        text=re.sub('0x'+format(old,'04X')+r'\b','0x'+format(new,'04X'),text)
    text=text.replace('#DE39','#CF07')
    exec(compile(text,'<verified_action_case_adapter>','exec'),namespace)
    return namespace[function.__name__]


def main():
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    original={i['address']:i for g in flow if g['name']=='Map' for i in g['instructions'] if i['slot']==7 and 0xD4E5<=i['address']<0xD8E2}
    flat=flat_action();rows=[dict(address=i.address,operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')]
    ops={i['address']:i for i in rows};assert len(original)==len(ops)
    changed_words=0
    # Сверка каждой инструкции, допустимы только явно установленные абсолютные адреса.
    for address,item in original.items():
        wanted=bytearray.fromhex(item['hex']);operation=item['operation'];match=re.search(r'#([0-9A-F]{4})',operation)
        if match:
            target=translated(int(match[1],16))
            assert len(wanted)==3 and wanted[0] in (0xCD,0xC4,0xC3,0xFA,0xF2,0xC2,0x21)
            wanted[1:]=target.to_bytes(2,'little');operation=operation[:match.start(1)]+format(target,'04X')+operation[match.end(1):];changed_words+=1
        actual=ops[translated(address)]
        assert actual['hex']==wanted.hex() and actual['operation']==operation,(hex(address),item,actual)
    pairs=json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_text('utf-8'))['rows']
    map_pairs=json.loads((ROOT/'Tools/Disasm/Reports/MapClipDispatch.json').read_text('utf-8'))['pairs']
    original_targets={(p['first'],p['second']):p['target'] for p in map_pairs}
    for p in pairs:assert p['target']==translated(original_targets[p['first_code']&15,p['second_code']&15])
    trace,expand=adapted(paths.paths),adapted(decisions.expand)
    roots=[]
    for target in sorted({p['target'] for p in pairs}):
        checked,ends=trace(target,ops);roots.append(dict(entry=target,abstract_states=checked,terminal_outcomes=sorted(ends)))
    cases=[dict(first=p['first_code']&15,second=p['second_code']&15,entry=p['target'],paths=expand(p['target'],ops)) for p in pairs]
    report=dict(passed=True,handler_bytes=1021,handler_instructions=len(rows),absolute_words_relocated=changed_words,
        physical_pairs=81,distinct_roots=len(roots),semantic_paths=sum(len(c['paths']) for c in cases),
        all_instruction_bytes_compared=True,initialized_products_proved=True,conditions_provenance_explained=True,
        special_exits_have_no_nested_case_calls=True,maximum_output_points_with_corner_block_1=2,
        independent_geometry_proof=False,all_final_registers_proved=False,assembly_executed=False,native_execution=False,roots=roots)
    for name,value in (('ActionClipCasePathsVerification',report),('ActionClipDecisionPaths',dict(cases=cases,independent_geometry_proof=False))):
        (ROOT/('Tools/Disasm/Reports/'+name+'.json')).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({k:v for k,v in report.items() if k!='roots'},indent=2))


if __name__=='__main__':main()
