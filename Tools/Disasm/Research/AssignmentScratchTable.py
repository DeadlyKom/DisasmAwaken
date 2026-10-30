"""Один физический шестибайтовый рабочий экземпляр присваивания в LANG."""
PATH='Source/Text/Data/AssignmentScratch.asm'


def render(source):
 values=[int.from_bytes(source[0xA7B+i:0xA7D+i],'little') for i in (0,2,4)]
 line=('Entry:'.ljust(16)+'FAssignmentExpression { '+', '.join('#'+format(v,'04X') for v in values)+' }').ljust(80)+'; Writer, Operator, Right, исходные рабочие слова'
 text='\n'.join(['                module AssignmentScratch','; Документация [присваивание](../../../Docs/AssignmentPipeline.md)',
  '                assert $ == #CA7B',line,'                assert $ == #CA81','                endmodule'])+'\n'
 symbols={'AssignmentScratch.Entry':0xCA7B}
 for field,offset in (('Writer',0),('Operator',2),('Right',4)):symbols['AssignmentScratch.Entry.'+field]=0xCA7B+offset
 return text,symbols
