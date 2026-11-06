"""Числовые эффекты IM 1 ROM без клавиш и с неактивными двумя KSTATE, без Z80-исполнения."""
def apply(read,put,registers,return_pc):
    stack=registers[12]

    def word(address,value):
        put(address,value&255);put(address+1,value>>8)

    # Создание аппаратного возврата и четырёх сохранённых регистров ROM.
    word(stack-2,return_pc)
    word(stack-4,registers[0]*256+registers[1])
    word(stack-6,registers[6]*256+registers[7])
    word(stack-8,registers[2]*256+registers[3])
    word(stack-10,registers[4]*256+registers[5])
    # Обновление младшего слова FRAMES, старший байт записывается только при переполнении слова.
    low=(read(0x5C78)+256*read(0x5C79)+1)&65535
    word(0x5C78,low)
    if low==0:put(0x5C7A,(read(0x5C7A)+1)&255)
    # Создание кадров трёх реальных CALL клавиатурной части ROM.
    word(stack-12,0x004D)
    word(stack-14,0x02C2)
    word(stack-14,0x02DB)
    return [0xFEFE,0xFDFE,0xFBFE,0xF7FE,0xEFFE,0xDFFE,0xBFFE,0x7FFE]
