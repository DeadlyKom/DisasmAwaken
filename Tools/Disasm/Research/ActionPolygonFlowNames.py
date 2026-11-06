"""Доказанные входы общих продолжений заполнителя, числовые шаблоны JP D100 не заменяются."""
import re
TARGETS={0xD229:'Action.PolygonFillRows.CheckRow',0xD22D:'Action.PolygonFillRows.DrawRow',
    0xD263:'Action.PolygonFillRows.RestoreStack',0xD268:'Action.SelectPolygonRightEdge.Entry',
    0xD26B:'Action.WrapPolygonLeftEdge.Entry',0xD27E:'Action.UpdatePolygonLeftEdge.ReadNextRow',
    0xD3A8:'Action.WrapPolygonRightEdge.Entry',0xD3BC:'Action.UpdatePolygonRightEdge.ReadNextRow',
    0xD4C1:'Action.SelectPolygonRowLimit.Entry',0xD4F5:'Action.SetShortNegativeRightStep.Entry',
    0xD503:'Action.WrapPolygonLeftTop.Entry',0xD50A:'Action.WrapPolygonRightTop.Entry',
    0xD50F:'Action.ReturnPolygonFill.Entry',0xD547:'Action.PreparePolygonFill.ReadLeftTop',
    0xD557:'Action.PreparePolygonFill.ReadRightTop'}


def name_operands(region,address,operation):
    if region=='Action' and 0xD1C0<=address<0xD5C9:
        match=re.match(r'^(?:CALL|JP|JR|DJNZ)\b.*#([0-9A-F]{4})$',operation)
        if match and int(match[1],16) in TARGETS:
            operation=operation[:match.start(1)-1]+'@'+TARGETS[int(match[1],16)]
    return operation
