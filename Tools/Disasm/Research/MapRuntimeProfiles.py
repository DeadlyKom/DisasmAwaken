"""Реестр оставшихся договоров только исходного профиля после проверки изменяемых байтов."""
GROUPS={
}
TEXT={
 'outcodes':'порог 255 в этом договоре относится к исходным CP, D0C3 заменяет его на (Max+1)&255',
 'products':'формулы с границами 0/255 относятся к исходным операндам BC, D0C3 меняет четыре граничных значения',
 'intersections':'договор фиксированных 0/255 и порога Y=192 описывает исходные операнды, D0C3 заменяет их параметрами окна',
 'corners':'указанные пары 0/255 относятся к исходным LD DE, D0C3 записывает фактические углы окна',
 'arc_columns':'колонки 30 и 1 относятся к исходным OR, D0C3 заменяет их значениями ColumnByte[MaxX] и ColumnByte[0]',
 'span_column':'колонка 1 относится к исходному OR, D0C3 записывает ColumnByte[0]',
 'seek_column':'OR 0 относится к исходному операнду, D0C3 записывает ColumnByte[MaxX], прежние синтетические 1/31 не проверяли полный установщик'}
GUARDS={address:TEXT[group]+', [фазы исполнения](../../Docs/MapRuntimeProfiles.md)' for group,addresses in GROUPS.items() for address in addresses}
DOCUMENTS={('Map',0xD0C3):('MapRuntimeProfiles','69 изменяемых байтов границ и параметров окна'),
 ('Map',0xDFC3):('MapRuntimeProfiles','выбор режима изменяемых условий хвостов')}


def qualify(contracts):
 for address,guard in GUARDS.items():
  inputs,outputs,corrupt,notes=contracts['Map',address]
  contracts['Map',address]=([guard,*inputs],outputs,corrupt,notes)
