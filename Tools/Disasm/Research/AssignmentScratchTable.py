"""Физическая запись присваивания и два следующих слова вложенного RHS в LANG."""
PATH='Source/Text/Data/AssignmentScratch.asm'
START = 0xA7B
NESTED_START = 0xA81
END = 0xA85


def render(source):
 values=[int.from_bytes(source[START+i:START+i+2],'little') for i in (0,2,4)]
 line=('Entry:'.ljust(16)+'FAssignmentExpression { '+', '.join('#'+format(v,'04X') for v in values)+' }').ljust(80)+'; Writer, Operator, Right, исходные рабочие слова'
 nested_values = [int.from_bytes(source[i:i + 2], 'little') for i in range(NESTED_START, END, 2)]
 nested = ('NestedTail:'.ljust(16) + 'FAssignmentNestedTail { ' +
           ', '.join(f'#{value:04X}' for value in nested_values) + ' }').ljust(80)
 text='\n'.join(['                module AssignmentScratch','; Документация [присваивание](../../../Docs/AssignmentPipeline.md)',
  '                assert $ == #CA7B',line,'                assert $ == #CA81',
  '                ; При RHS в скобках временный левый операнд занимает Entry.Right.',
  nested + '; Operator, Right вложенного выражения, исходные рабочие слова',
  '                assert $ == #CA85','                endmodule'])+'\n'
 symbols={'AssignmentScratch.Entry':0xCA7B}
 for field,offset in (('Writer',0),('Operator',2),('Right',4)):symbols['AssignmentScratch.Entry.'+field]=0xCA7B+offset
 symbols.update({'AssignmentScratch.NestedTail': 0xCA81, 'AssignmentScratch.NestedTail.Operator': 0xCA81,
                 'AssignmentScratch.NestedTail.Right': 0xCA83})
 return text,symbols
