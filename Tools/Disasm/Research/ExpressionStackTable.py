"""Двадцать физических байтов между таблицей токенов и записью присваивания."""
PATH='Source/Text/Data/ExpressionStack.asm'


def render(source):
 raw=source[0xA67:0xA7B]
 if len(raw)!=20:raise ValueError('Неверный исходный диапазон стека выражений')
 values=[int.from_bytes(raw[i:i+2],'little') for i in range(0,20,2)]
 line=('Entry:'.ljust(16)+'FExpressionStackStorage { '+', '.join('#'+format(v,'04X') for v in values)+' }')
 # Описание всех десяти слов вынесено перед длинным физическим инициализатором.
 text='\n'.join(['                module ExpressionStack','; Документация [стек выражений](../../../Docs/ExpressionStack.md)',
  '                assert $ == #CA67','                ; исходные Word00..Word09, порядок и начальные значения сохранены',
  line,'                assert $ == #CA7B','                endmodule'])+'\n'
 symbols={'ExpressionStack.Entry':0xCA67}
 symbols.update({'ExpressionStack.Entry.Word'+format(i,'02d'):0xCA67+2*i for i in range(10)})
 return text,symbols
