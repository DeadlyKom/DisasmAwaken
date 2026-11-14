"""Уточнение трёх доказанных разрядов LinkFlags, без изменения физической структуры или данных."""
import contextlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
from ActionObjectRecords import parse


def main():
    old='бит 1 устанавливается при создании связи с ракетой, остальные разряды ещё неизвестны'
    new='бит 0 задаёт обратную связь E804, бит 1 установленную связь создателя или State08, бит 2 ближнюю область State08, биты 7..3 неизвестны'
    pending={};counts={}
    for relative,count in (('Tools/Disasm/Research/ActionObjectRecords.py',1),('Includes/Structs/Include.inc',1),('Source/Action/Data/ObjectRecords.asm',26)):
        path=ROOT/relative;text=path.read_text('utf-8');assert text.count(old)==count
        text=text.replace(old,new)
        text=text.replace('Разряды 7..0, ? ? ? ? ? ? L ?, L занимает бит 1, маска 02','Разряды 7..0, ? ? ? ? ? A L B, маски B=01, L=02, A=04')
        text=text.replace('L устанавливается при записи LinkedIndex из 60AE, потребители ещё не полностью разобраны','B задаёт обратную ссылку E804, L запись связи создателем или State08, A ближнюю область State08')
        text=text.replace('Ноль сбрасывает L и неизвестные разряды, отсутствие живой связи одним этим не доказывается','Ноль сбрасывает три известных признака и неизвестные биты, отсутствие живой связи этим не доказывается')
        pending[path]=text.encode('utf-8');counts[relative]=count
    physical=ROOT/'Source/Action/Data/ObjectRecords.asm';assert parse(physical.read_text('utf-8'))==parse(pending[physical].decode('utf-8'))
    path=ROOT/'Docs/ActionObjectRecords.md';text=path.read_text('utf-8')
    text=text.replace('Бит 1 устанавливается при этой записи связи, остальные разряды пока неизвестны','Три контекстных признака в битах 0, 1 и 2, остальные пять не установлены')
    begin=text.index('Разряды 7..0 имеют схему');end=text.index('\nПри создании ракеты',begin)
    text=text[:begin]+'''Разряды 7..0 имеют схему `? ? ? ? ? A L B`. Это независимые признаки в опубликованных контекстах, назначение разрядов 7..3 не выдумывается.

| Бит и маска | Доказанный писатель и условие |
| --- | --- |
| 0, B, 01 | [CheckAndToggleLinkedOverlay](ActionLinkedOverlay.md) устанавливает перед обратной записью LinkedIndex, если прочитанный R не меньше порога |
| 1, L, 02 | [CreateLinkedMissileRecord](ActionClass17Spawn.md) устанавливает при создании связи цели с ребёнком, [State08](ActionArrivalState.md) до проверки активности выбранной цели |
| 2, A, 04 | State08 устанавливает после нулевого накопителя остаточных старших байтов, то есть попадания в его ближнюю область |

Бит 0 записывается до проверок знаков и переполнений, их отказ его не отменяет. Бит 1 State08 ставится даже у записи, которая затем окажется недоступной. Бит 2 ставится и при StateCode цели FF, это значение запрещает только освобождение текущей записи. Поэтому ни один из трёх битов сам по себе не доказывает наличие доступной живой цели.

Полный ноль сбрасывает три известных признака и пять неизвестных разрядов. Создатели могут записать весь нулевой байт при инициализации. Полный разбор всех игровых потребителей остаётся отдельной задачей. Физический формат FActionRecord, все 26 экземпляров и 1664 исходных байта сохранены.
'''+text[end:]
    pending[path]=text.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionLinkFlagsRoles';history=ROOT/'Tools/Disasm/Research/History/BeforeActionLinkFlagsRoles'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes(),a) for p,a in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before
    for path,before,after in plan:
        target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before);path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    result=dict(passed=True,changed_note_counts=counts,known_bit_masks=[1,2,4],unknown_bits=[3,4,5,6,7],physical_record_bytes_unchanged=1664,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionLinkFlagsRolesVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
