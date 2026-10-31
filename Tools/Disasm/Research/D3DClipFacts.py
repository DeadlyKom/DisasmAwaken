"""Точная настройка существующих операндов границ D3D банка 4."""
FUNCTIONS={0xE011:('ConfigurePreviewClip','Настройка четырёх углов и повторённых операндов границ корабельного просмотра')}
LABELS={}
DOCUMENTS={('D3D',0xE011):('PreviewClipBounds','байтовые пределы, повторённые операнды, углы и сохранённый Carry')}
PATCHES={0xDAE7:'HalfXLow',0xDBA5:'HalfYLow',0xE7DB:'MaxCorner',0xE7BA:'MinCorner',0xE7D0:'MaxXMinY',0xE7C5:'MinXMaxY',0xDF7F:'AfterMaxX',0xDF64:'AfterMaxY'}
for prefix,addresses in (('MaxX',(0xE613,0xE6E0,0xE6F3,0xE72E,0xE78B)),('MinX',(0xE5F4,0xE695,0xE6A8,0xE73F,0xE79C)),('MaxY',(0xE646,0xE69D,0xE6E8,0xE788,0xE799,0xE7AB)),('MinY',(0xE627,0xE692,0xE6DD,0xE72B,0xE73C,0xE74E))):
 for i,address in enumerate(addresses):PATCHES[address]=prefix+str(i)
PATCH_FORMS={}
for address,name in PATCHES.items():
 if name in ('HalfYLow','MaxCorner','MinCorner','MaxXMinY','MinXMaxY'):opcode,kind=0x11,'LD DE,nn'
 elif name.startswith('After'):opcode,kind=0xFE,'CP n'
 elif name in ('HalfXLow','MaxX0','MinX0','MaxY0','MinY0'):opcode,kind=1,'LD BC,nn'
 elif name in ('MaxY1','MaxY2'):opcode,kind=0x2E,'LD L,n'
 else:opcode,kind=0x36,'LD (HL),n'
 PATCH_FORMS[address]=(opcode,kind,2 if name in ('MaxCorner','MinCorner','MaxXMinY','MinXMaxY') else 1)
CONTRACTS={('D3D',0xE011):(
 ['HL - H верхний предел X, L верхний предел Y, DE - D нижний предел X, E нижний предел Y, все компоненты байтовые',
  'подключён исходный D3D в банке 4, существующие операнды графического ядра доступны для записи'],
 ['HL - H исходный верхний X, L исходный нижний Y, DE - D исходный нижний X, E исходный верхний Y, BC сохранён',
  'AF - A исходный нижний Y, F от INC исходного верхнего Y, Carry равен биту 0 суммы верхний Y+1 по модулю 256',
  'четыре упакованных угла и повторённые граничные операнды настроены, полупределы равны ((верхняя компонента+1) AND FF) SHR 1',
  'альтернативные и индексные регистры, I, IFF и IM сохранены, SP обычного возврата равен входному SP+2'],
 ['HL, DE, AF'],
 ['верхний X берётся из ширины текстового окна минус 14, верхний Y из высоты минус 13 в исходном DrawItem26, нижние пределы там нулевые',
  'процедура не проверяет порядок границ и не включает нижние пределы в расчёт полупределов',
  'при верхнем пределе FF прибавление единицы оборачивается в ноль до деления, это исходное поведение',
  'полупределы и первые копии X и Y меняют младшие байты слов, остальные копии меняют байтовые операнды LD (HL),n или LD L,n',
  'всего меняются 34 байта существующих операндов в банке 4, экран, порт страниц и стековая память не записываются'])}
COMMENTS={0xE011:(['-----------------------------------------','Полупределы и четыре угла','-----------------------------------------','расчёт байтового полупредела X с исходным оборачиванием FF в ноль'],None),
 0xE018:(['расчёт байтового полупредела Y, младший бит суммы останется в Carry до возврата'],None),
 0xE01F:(['сохранение углов с одновременно верхними и одновременно нижними компонентами'],None),
 0xE026:(['перестановка только младших компонент для двух остальных углов'],None),
 0xE030:(['-----------------------------------------','Повторённые операнды пределов','-----------------------------------------','обновление копий верхнего X и исключённого предела X+1'],None),
 0xE044:(['обновление копий нижнего X, меняются только указанные байтовые операнды'],None),
 0xE054:(['обновление копий верхнего Y и исключённого предела Y+1'],None),
 0xE06B:(['обновление копий нижнего Y без изменения флагов последнего INC верхнего Y'],None)}


def name_operands(region,address,operation):
 if region=='D3D' and address==0xE011:
  for value,name in PATCHES.items():operation=operation.replace('(#'+format(value,'04X')+')','(@D3DClipState.'+name+')')
 return operation

from D3DThirdFacts import COMMENTS as THIRD_COMMENTS
COMMENTS.update(THIRD_COMMENTS)

from D3DSetupFacts import COMMENTS as SETUP_COMMENTS
COMMENTS.update(SETUP_COMMENTS)

from D3DDescriptionFacts import COMMENTS as DESCRIPTION_COMMENTS
COMMENTS.update(DESCRIPTION_COMMENTS)

from D3DPriceFacts import COMMENTS as PRICE_COMMENTS
COMMENTS.update(PRICE_COMMENTS)

from PreviewMultiplyFacts import COMMENTS as PREVIEW_MULTIPLY_COMMENTS
COMMENTS.update(PREVIEW_MULTIPLY_COMMENTS)

from PreviewTransformFacts import COMMENTS as PREVIEW_TRANSFORM_COMMENTS
COMMENTS.update(PREVIEW_TRANSFORM_COMMENTS)
