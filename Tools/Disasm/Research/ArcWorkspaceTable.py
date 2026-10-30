"""Физический снимок 24 байтов рабочего состояния дуги, исходные ненулевые значения сохранены."""
DATA='Source/Map/Data/ArcWorkspace.asm'
FIELDS=(('AbsY',1),('AbsX',1),('QuadrantCode',1),('Radius',1),('OffsetY',1),('OffsetX',1),('RowY',1),('CenterX',1),('StartY',1),
 ('RasterStack',2),('SqrtTarget',2),('LeftMask',1),('RasterDown',1),('UpperRow',2),('LowerRow',2),
 ('MaxY',1),('ReferenceX',1),('HalfY',1),('HalfXLimit',1),('HalfXSquare',1))
ORIGINAL=bytes.fromhex('00 00 0f 28 00 00 00 00 00 00 00 00 00 00 00 00 40 00 58 00 00 00 00 00')


def render(source):
 if source[0x1FAB:0x1FC3]!=ORIGINAL:raise ValueError('Изменён исходный снимок рабочего состояния дуги')
 values=[];symbols={'MapArcWork.State':0xDFAB};cursor=0
 for field,width in FIELDS:
  symbols['MapArcWork.State.'+field]=0xDFAB+cursor;value=int.from_bytes(ORIGINAL[cursor:cursor+width],'little')
  values.append('#'+format(value,'04X' if width==2 else '02X'));cursor+=width
 assert cursor==24
 text='\n'.join(['                module MapArcWork',
  '; Документация [поля и исходные значения состояния дуги](../../../Docs/ArcWorkspace.md)',
  '                assert $ == #DFAB',
  '                ; AbsY=0, AbsX=0, QuadrantCode=0F с неизвестными старшими битами, Radius=28',
  '                ; OffsetY, OffsetX, RowY, CenterX, StartY исходно нулевые',
  '                ; RasterStack=0, SqrtTarget=0, LeftMask=0, RasterDown=0',
  '                ; UpperRow=4000, LowerRow=5800, это исходные адреса до настройки окна',
  '                ; MaxY, ReferenceX, HalfY и обе копии HalfX исходно нулевые',
  'State:'.ljust(16)+'FMapArcWorkspace { '+', '.join(values)+' }',
  '                assert $ == #DFC3','                endmodule'])+'\n'
 return {DATA:text},symbols
