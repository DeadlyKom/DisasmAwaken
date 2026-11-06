"""Точечная публикация сведения координат и шести исходных изменяемых операндов."""
import ActionClampVectorWordsFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionClampVectorWords','ActionClampVectorWords',state_fields=(
        ('FirstHigh',0x7F0F,'старшее слово первого signed32, младший байт задаёт исходный бит 23'),
        ('FirstLow',0x7F12,'младшее слово первого signed32'),
        ('SecondHigh',0x7F23,'старшее слово второго signed32, младший байт задаёт исходный бит 23'),
        ('SecondLow',0x7F26,'младшее слово второго signed32'),
        ('ThirdHigh',0x7F37,'старшее слово третьего signed32, младший байт задаёт исходный бит 23'),
        ('ThirdLow',0x7F3A,'младшее слово третьего signed32')),include_blocks=(
        ('Includes/Const/Include.inc','module ActionClampWordsConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FClampVectorFrame',facts.STRUCT_BLOCK)))
