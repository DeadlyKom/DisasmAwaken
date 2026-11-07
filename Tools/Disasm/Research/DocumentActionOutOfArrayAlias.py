"""Фиксация причины расхождения эталона и расширенных профилей без правки игры."""
import json
from CheckIntro import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports'
    for tag,count in (('ActionLinkedTargetState',44656),('ActionLinkedPhaseState',44032)):
        proof=json.loads((reports/(tag+'UnrestrictedVerification.json')).read_text('utf-8'))
        assert proof['passed'] and proof['total_cases']==count and proof['unrestricted_out_of_array_overlay_profile_proved']
        assert not proof['out_of_record_array_profiles_use_current_overlay_marker']
    pending={}
    replacements=(
        ('для индексов за массивом проход к экранному помощнику проверен с исходным маркером текущего контекста, неограниченный экранный профиль имеет отдельное неразрешённое расхождение модели',
         'дополнительно прошли 44656 профилей без маркера отказа за массивом, учтена запись индекса текущей записи поверх JR NZ по C94B'),
        ('вне массива записей экранный профиль ограничен исходным маркером текущего контекста, косвенный следующий обработчик и общий F0F8 не исполнялись',
         'дополнительно прошли 44032 профиля без маркера отказа за массивом, косвенный следующий обработчик и общий F0F8 не исполнялись'),
        ('полное произведение входов, неограниченный экранный профиль за массивом, R/T растеризатора',
         'полное произведение входов, произвольные изменения кода индексом за массивом, R/T растеризатора'),
    )
    for name in ('Tools/Disasm/Research/ActionLinkedTargetStateFacts.py','Tools/Disasm/Research/ActionLinkedPhaseStateFacts.py',
                 'Source/Action/HandleLinkedTargetState.asm','Source/Action/HandleLinkedPhaseState.asm'):
        path=ROOT/name;before=path.read_bytes();text=before.decode('utf-8')
        for old,new in replacements:
            if old in text:text=text.replace(old,new)
        assert text!=before.decode('utf-8'),name
        pending[path]=(before,text.encode('utf-8'))
    path=ROOT/'Docs/ActionLinkedTargetState.md';before=path.read_bytes();text=before.decode('utf-8')
    paragraphs=text.split('\n\n');indices=[i for i,p in enumerate(paragraphs) if p.startswith('Индексы 1B..FE')];assert len(indices)==1
    paragraphs[indices[0]]='Индексы 1B..FE находятся вне исходного массива и могут обращаться к кодовой RAM как к данным. Дополнительные 44656 профилей без маркера отказа прошли после уточнения модели, включая 23 экранных вызова и глубину стека 28 байтов. Причина прежнего расхождения установлена [по фактической записи в код](ActionOutOfArrayCodeAlias.md). Косвенный следующий обработчик и общий F0F8 по-прежнему не исполняются.'
    text='\n\n'.join(paragraphs).replace('общий F0F8, неограниченный экранный профиль за массивом, R/T растеризатора',
        'общий F0F8, произвольные варианты изменения кода за массивом, R/T растеризатора')
    pending[path]=(before,text.encode('utf-8'))
    path=ROOT/'Docs/ActionLinkedPhaseState.md';before=path.read_bytes();text=before.decode('utf-8')
    paragraphs=text.split('\n\n');indices=[i for i,p in enumerate(paragraphs) if p.startswith('Для индексов вне массива')];assert len(indices)==1
    paragraphs[indices[0]]='Дополнительно прошли 44032 профиля без маркера отказа за массивом, включая 62 экранных вызова и глубину стека 28 байтов. [Причина прежнего расхождения модели](ActionOutOfArrayCodeAlias.md) установлена и учтена. Косвенный следующий обработчик и общий F0F8 не исполнялись. Полное произведение входов, произвольные изменения кода индексом за массивом, R/T растеризатора, аппаратные IRQ, сборка и нативная игра не доказаны.'
    pending[path]=(before,'\n\n'.join(paragraphs).encode('utf-8'))
    path=reports/'ActionLinkedTargetOutOfArrayLimitation.json';before=path.read_bytes();record=json.loads(before)
    assert record['resolved'] is False
    record.update(resolved=True,resolution='Числовая модель предполагала неизменный JR NZ по C94B, но E804 при IY=C940 записывает туда индекс текущей записи 18, получается безусловный JR с прежним смещением 27',
        actual_code_write=dict(writer=0xE832,target=0xC94B,old_byte=0x20,new_byte=0x18),
        supported_modified_dispatch=dict(branch_opcodes=[0x20,0x18],relative_offset=0x27),
        unrestricted_out_of_array_overlay_profile_proved=True,
        current_passing_profile_uses_current_overlay_marker_for_out_of_array_indices=False,
        arbitrary_out_of_array_code_mutations_proved=False,
        historical_mismatches_preserved_above=True,original_game_bytes_modified=False,
        verification_reports=['Tools/Disasm/Reports/ActionLinkedTargetStateUnrestrictedVerification.json',
                              'Tools/Disasm/Reports/ActionLinkedPhaseStateUnrestrictedVerification.json'])
    pending[path]=(before,(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    # Создание отдельного кандидата и проверка исходных версий всех затронутых файлов.
    for prefix,part in (('Candidates/ActionOutOfArrayAlias',1),('History/BeforeActionOutOfArrayAlias',0)):
        folder=ROOT/'Tools/Disasm/Research'/prefix;assert not folder.exists()
        for path,values in pending.items():
            target=folder/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(values[part])
    for path,(before,after) in pending.items():assert path.read_bytes()==before
    for path,(before,after) in pending.items():path.write_bytes(after)
    print(json.dumps(dict(passed=True,files=len(pending),original_game_bytes_modified=False,assembly_executed=False)))


if __name__=='__main__':main()
