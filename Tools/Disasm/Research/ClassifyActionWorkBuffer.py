"""Замена неизвестного контракта уже именованной процедуры без смены её имени и инструкций."""
from ClassifyActionRegionType import main
import ActionWorkBufferFacts as facts

if __name__=='__main__':
    block='\n                module ActionWorkBufferConst\n'
    for name,value,note in (('BufferEnd',0x8C00,'исключённый верхний адрес 96 линейных строк'),
        ('FillWord',0xFFFF,'два исходных байта заполнения FF'),('BlockCount',0x60,'96 блоков по 16 PUSH и 32 байта')):
        block+=(name.ljust(16)+'equ #'+format(value,'04X' if value>255 else '02X')).ljust(80)+'; '+note+'\n'
    block+='                endmodule\n'
    main(facts,'ActionWorkBuffer','ActionWorkBuffer',(('SavedSP',0xD129,'операнд LD SP,nn, исходный CPU SP перед временной записью буфера'),),
        allow_named=True,include_blocks=(('Includes/Const/Include.inc','module ActionWorkBufferConst',block),))
