"""Публикация доказанного формата заметок, потребитель в игре этим не объявляется установленным."""
from collections import Counter
import contextlib,hashlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';read=lambda stem:json.loads((reports/(stem+'.json')).read_bytes())
    proof=read('ActionEmbeddedNotesVerification');assert proof['passed'] and proof['length']==3729
    sm,inventory=read('SourceMap'),read('Inventory');row=next(r for r in sm if r['slot']==17 and r['offset']==0x516F)
    assert row['length']==3729 and row['kind']=='unclassified'
    old=ROOT/row['path'];raw=old.read_bytes();assert hashlib.sha256(raw).hexdigest()==proof['sha256']
    new='Source/Resources/17_ACTION/EmbeddedAuthorNotes.bin';assert not (ROOT/new).exists()
    row.update(path=new,kind='binary_resource');inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm))
    inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    pending={ROOT/new:raw,reports/'SourceMap.json':encode(sm),reports/'Inventory.json':encode(inventory)}
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old.name+'"';assert text.count(needle)==1
    pending[path]=text.replace(needle,'                ; Фрагмент авторских заметок CP866, потребитель в игре не установлен\n                ; Документация [формат и происхождение](../../Docs/ActionEmbeddedNotes.md)\n                incbin "../Resources/17_ACTION/EmbeddedAuthorNotes.bin"').encode('utf-8')
    path=ROOT/'Docs/ActionEmbeddedNotes.md';text=path.read_text('utf-8')
    needle='сохранён, его размещение, байты и статус неразмеченного диапазона\nне менялись.';assert text.count(needle)==1
    text=text.replace(needle,'сохранён как [EmbeddedAuthorNotes.bin](../'+new+'), формат фрагмента авторских заметок CP866 подтверждён. Размещение и все 3729 байтов сохранены, диапазон классифицирован как бинарный ресурс с доказанным текстовым форматом.')
    text+='\n[Повторная проверка](../Tools/Disasm/Reports/ActionEmbeddedNotesVerification.json) сохраняет исходный реестр исследования и проверяет текущий путь ресурса. Классификация формата не доказывает отсутствие исполнения или чтения во время игры и не устанавливает ещё неизвестных потребителей.\n'
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    binary_resources[7, 0x2900]';assert text.count(needle)==1
    hook='    # Формат исходного фрагмента заметок доказан, игровой потребитель остаётся неизвестным.\n    binary_resources[17,0x516F]=(0x6000,"'+new+'","CP866_AUTHOR_NOTES_FRAGMENT")\n'
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionEmbeddedNotesResource';history=ROOT/'Tools/Disasm/Research/History/BeforeActionEmbeddedNotesResource'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        target=candidate/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before in {**{p:b for p,b,_ in plan if b is not None},old:raw}.items():
        target=history/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve()) and old.read_bytes()==(history/old.relative_to(ROOT)).read_bytes();old.unlink()
    result=dict(passed=True,typed_format='fragmentary_author_notes_cp866',resource_bytes=3729,original_bytes_and_layout_preserved=True,
        live_game_consumer_proved=False,complete_document_present=False,assembly_executed=False,native_execution=False)
    (reports/'ActionEmbeddedNotesResourceClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
