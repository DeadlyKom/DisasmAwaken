"""Охват отдельных клавиатурных указателей, последнее перекрывающееся слово учитывается отдельно."""
import hashlib,json
from CheckIntro import ROOT


def audit():
    reports=ROOT/'Tools/Disasm/Reports'
    functions=json.loads((reports/'Functions.json').read_bytes());source_map=json.loads((reports/'SourceMap.json').read_bytes())
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry=next(e for e in manifest['entries'] if e['slot']==17)
    image=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    raw=(ROOT/(entry['path']+'.bin')).read_bytes();assert raw==image[entry['offset']:entry['offset']+len(raw)]
    rows=[]
    # Проверка всех 26 физических слов, загруженное ядро 6000..7F8E имеет смещение переноса 23D.
    for index in range(26):
        target=int.from_bytes(raw[0x1254+2*index:0x1256+2*index],'little')
        assert 0x6000<=target<0xC000
        offset=target-0x6000+(0x23D if target<0x7F8F else 0)
        ranges=[r for r in source_map if r['slot']==17 and r['offset']<=offset<r['offset']+r['length']]
        assert len(ranges)==1
        owners=[f for f in functions if f['region']=='Action' and f['address']==target and f['offset']==offset]
        assert len(owners)<=1
        rows.append(dict(index=index,target=target,file_offset=offset,registered=bool(owners),
            function=owners[0]['name'] if owners else None,physical_path=ranges[0]['path'],physical_kind=ranges[0]['kind']))
    # Проверка слова, которое диспетчер читает за пределами 26 физических записей.
    overlap=raw[0x1288:0x128A];assert overlap==bytes.fromhex('c9 c0')
    pending=[r for r in rows if not r['registered']]
    overlap_step = dict(index=26, word=0xC0C9, bytes=overlap.hex(),
                        separate_physical_record=False, bank_context_and_intended_handler_proved=False)
    dispatch_report = reports / 'ActionOverlappingKeyDispatchVerification.json'
    returns_report = reports / 'ActionOverlappingKeyClipReturnsVerification.json'
    if dispatch_report.exists() and returns_report.exists():
        dispatch = json.loads(dispatch_report.read_bytes())
        returns = json.loads(returns_report.read_bytes())
        assert dispatch['passed'] and returns['passed']
        assert dispatch['actual_bank'] == 0 and dispatch['original_27th_word'] == 0xC0C9
        assert dispatch['actual_target'] == 'Action.ClipInsideToTopLeft.Entry'
        assert returns['original_keyboard_frame_used_without_substitution']
        overlap_step.update(actual_bank_in_stationary_FD_02_profile=0,
                            actual_target_in_that_profile=dispatch['actual_target'],
                            prepared_clip_returns_proved=True,
                            author_intent_proved=False)
    frame_report = reports / 'ActionInitializedKeyClipVerification.json'
    if frame_report.exists():
        frames = json.loads(frame_report.read_bytes())
        assert frames['passed'] and frames['coordinates_unchanged_by_probe']
        overlap_step.update(initialized_frame_probes=frames['total_cases'],
                            all_runtime_clip_states_proved=False)
    return dict(passed=True,table_entries=26,registered_entries=26-len(pending),unregistered_entries=len(pending),
        entries=rows,unregistered_targets=pending,all_separate_handlers_registered=not pending,
        overlapping_step=overlap_step,
        source_map_sha256=hashlib.sha256((reports/'SourceMap.json').read_bytes()).hexdigest(),
        all_keyboard_algorithms_proved=False,assembly_executed=False,native_execution=False)


def main():
    result=audit();(ROOT/'Tools/Disasm/Reports/ActionKeyboardCoverage.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('entries','unregistered_targets')},indent=2))


if __name__=='__main__':main()
