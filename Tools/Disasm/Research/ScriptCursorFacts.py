"""Имена доказанных обращений к символам курсора в уже разобранных входах."""
ADDRESSES={0xC000,0xC00C,0xC01B,0xC039,0xC057,0xC32C,0xC7B6,0xC7C3,0xC7D0,0xC7EE}


def name_operands(region,address,operation):
 if region=='Text' and address in ADDRESSES:
  return operation.replace('(IX + #00)','(IX + @ScriptConst.Cursor)').replace('(IX + #01)','(IX + @ScriptConst.NextChar)').replace('(IX - #01)','(IX - @ScriptConst.SuffixBack)').replace('LD HL, #CA67','LD HL, @ExpressionStack.Entry')
 return operation
