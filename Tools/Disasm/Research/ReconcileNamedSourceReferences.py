"""Согласование доказанных имён в комментариях и путях реестра изменяемого кода."""
import json
import os
from pathlib import Path
import tempfile
from CheckIntro import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    records=json.loads((reports/'ModifiedCode.json').read_text('utf-8'))
    source_map=json.loads((reports/'SourceMap.json').read_text('utf-8'))
    fixed=[]
    for item in records:
        if 'target_path' not in item or (ROOT/item['target_path']).is_file():continue
        matches=[row for row in source_map if row['slot']==item['target_slot']
                 and row['offset']<=item['target_offset']
                 and item['target_offset']+item['size']<=row['offset']+row['length']]
        assert len(matches)==1 and matches[0]['kind']=='code'
        fixed.append(dict(region=item['region'],writer=item['writer'],before=item['target_path'],after=matches[0]['path']))
        item['target_path']=matches[0]['path']
    assert len(fixed)==16
    pending={reports/'ModifiedCode.json':(json.dumps(records,ensure_ascii=False,indent=2)+'\n').encode('utf-8')}
    for name in ('CheckPreferredRandomWord','ContinuePreferredClass0','ContinuePreferredClass7',
                 'FindPreferredClass0','FindPreferredClass5','FindPreferredClass7','UpdatePreferredClass18'):
        path=ROOT/f'Source/Action/{name}.asm'
        text=path.read_text('utf-8')
        assert 'Unknown0A' in text
        pending[path]=text.replace('Unknown0A','StateCode').encode('utf-8')
    for filename,before,after in (
        ('Source/Action/CaptureProjectedRecord.asm','UnknownE36A.asm','FollowProjectedTarget.asm'),
        ('Source/Action/PrepareRecordScale.asm','UnknownE5A0.asm','UpdateRecordComponents.asm'),
        ('Source/Music/OutputAyFrame.asm','UnknownE37C.asm','AdvancePatternBC.asm'),
        ('Source/Music/StageOrnamentA.asm','UnknownDEB9.asm','StageChannelBRow.asm'),
        ('Tools/Disasm/Research/ActionRecordScaleFacts.py','UnknownE5A0.asm','UpdateRecordComponents.asm'),
        ('Tools/Disasm/Research/ActionOffsetRestoreFacts.py','UnknownE5A0.asm','UpdateRecordComponents.asm')):
        path=ROOT/filename;text=path.read_text('utf-8');assert before in text
        pending[path]=text.replace(before,after).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/NamedSourceReferences'
    history=ROOT/'Tools/Disasm/Research/History/BeforeNamedSourceReferences'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() for path in pending}
    for path,data in pending.items():
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    # Проверка сохранности рабочей копии перед публикацией, индекс Git не меняется.
    for path,data in before.items():
        assert path.read_bytes()==data
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for path,data in pending.items():
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='source-references-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name);output.write(data)
            try:os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(data)
    (reports/'NamedSourceReferenceReconciliation.json').write_text(json.dumps(dict(
        passed=True,modified_code_paths_fixed=fixed,comment_and_fact_files_updated=len(pending)-1,
        no_instructions_or_physical_data_changed=True,assembly_executed=False),indent=2)+'\n',encoding='utf-8')
    print('Исправлены 16 устаревших целевых путей и 13 файлов комментариев и действующих фактов')


if __name__=='__main__':main()
