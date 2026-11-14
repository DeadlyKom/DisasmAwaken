"""Побайтовое основание разбора отдельной копии, без смешивания дисковых смещений."""
import contextlib,hashlib,io,json,re
from ClassifyControlsTextDisplay import ROOT
from Contracts import CONTRACTS
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    source=ROOT/'Tools/Disasm/Extracted/Active'
    action=(source/'17_ACTION.C.bin').read_bytes();overlay=(source/'19_3DPART.C.bin').read_bytes()
    assert len(overlay)==8224 and overlay==action[0x6000:0x8020]
    functions=read('Functions')
    primary=[f for f in functions if f['region']=='Action' and 0xC000<=f['address']<0xE020]
    copies=[f for f in functions if f['region']=='ThreeD']
    assert (len(primary), len(copies)) in ((122, 98), (122, 122), (121, 121))
    proved=[f for f in primary if f['semantic_status']=='described']
    assert len(proved)==121 and all(('Action',f['address']) in CONTRACTS for f in proved)
    if len(copies) in (121, 122):
        # Повторная проверка уже опубликованной копии, прежняя проверка ручных комментариев остаётся историческим входным снимком.
        assert all((a['address'],a['name'],a['offset']-0x6000,a['end_offset']-0x6000,a['semantic_status'])==
                   (b['address'],b['name'],b['offset'],b['end_offset'],b['semantic_status']) for a,b in zip(primary,copies))
        report=read('ThreeDOverlayMirrorVerification')
        assert report['passed'] and report['sha256']==hashlib.sha256(overlay).hexdigest()
        report.update(current_fragments=len(copies),current_described=len(proved),
                      current_unknown=len(copies)-len(proved),rechecked_after_publication=True,
                      cf08_emitted_as_pointer_low_bytes=len(copies)==121,
                      current_source_instructions_and_data_verified=True,assembly_executed=False)
        (ROOT/'Tools/Disasm/Reports/ThreeDOverlayMirrorVerification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
        print(json.dumps(dict(passed=True,logical_bytes=8224,current_fragments=len(copies),
                              current_unknown=len(copies)-len(proved),rechecked_after_publication=True),indent=2))
        return
    allowed={'In:','Out:','Corrupt:','Note:','Unknown, регистровый контракт ещё не доказан',
        'исходный поток управления, включая переходы в соседние фрагменты',
        "HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница",
        'граница файла не доказывает границу логической процедуры',
        'состояние самомодификации и активной страницы учитывается отдельно'}
    # Проверка ручных пояснений до подготовки кандидата, незнакомые комментарии запрещают автоматическую замену.
    extra=[];prior_contracts=[]
    for function in copies:
        text=(ROOT/function['path']).read_text('utf-8');header,_,body=text.partition('Entry:')
        assert body
        old_contract=CONTRACTS.get(('ThreeD',function['address']))
        local_allowed=set(allowed)
        if old_contract:
            local_allowed.update(value for group in old_contract for value in group)
            prior_contracts.append(dict(name=function['name'],path=function['path'],contract=old_contract))
        else:
            assert 'Unknown, регистровый контракт ещё не доказан' in header
        for line in header.splitlines():
            if ';' not in line:continue
            note=line.partition(';')[2].strip()
            if not note or note in local_allowed or note==function['description'] or set(note)=={'-'}:continue
            if note.startswith(('Документация [ThreeD]','исходная запись 19, файловые смещения #')):continue
            extra.append(dict(path=function['path'],comment=note))
        for line in body.splitlines():
            if ';' not in line:continue
            note=line.partition(';')[2].strip()
            if note and not note.startswith(('переход, если флаг','выход, если флаг','вызов, если флаг','JP ')):
                extra.append(dict(path=function['path'],comment=note))
    assert not extra,extra
    report=dict(passed=True,source_slot=17,source_offset=0x6000,target_slot=19,target_offset=0,
        logical_bytes_compared=8224,byte_identical=True,sha256=hashlib.sha256(overlay).hexdigest(),
        target_load_address=0xC000,required_runtime_bank=0,
        primary_function_fragments=122,proved_primary_contracts=121,preserved_unknown=['UnknownCF08'],
        old_fragments=98,old_unproved_template_contracts=98-len(prior_contracts),prior_documented_contracts=prior_contracts,
        unrecognized_manual_comments=extra,all_external_RAM_and_entry_contexts_must_match=True,
        native_loading_of_separate_3DPART_not_executed=True,assembly_executed=False,
        original_header_split_boundaries_replaced_by_proved_primary_layout=True)
    (ROOT/'Tools/Disasm/Reports/ThreeDOverlayMirrorVerification.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
