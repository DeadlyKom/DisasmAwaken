"""Композиция независимых коэффициентов и трёх произведений, без исполнения Z80."""
from CheckActionObjectOffsetVector import table_reference,multiply,cost,COEFFICIENT_OPERANDS,RESULT_WORDS
from ReferenceControlsPointRespawn import refresh


def evaluate(memory,initial,offsets,return_address):
    value=initial[4]*256+initial[5];stack=initial[12];ix=initial[8]*256+initial[9]
    registers,coefficients,m1,overflow=table_reference(memory,initial,offsets)
    writes=list(zip(COEFFICIENT_OPERANDS,coefficients))
    # Создание числового эталона всех остаточных слов CPU-стека, включая повторные PUSH DE.
    for address,word in ((stack-2,ix),(stack-4,value),(stack-6,0x6D0C),(stack-4,value),(stack-4,value)):
        writes.extend(((address,word&255),(address+1,word>>8)))
    for address,coefficient in zip(RESULT_WORDS,coefficients):
        result,local_m1=multiply(registers,coefficient,value);m1+=local_m1
        writes.extend(((address,result&255),(address+1,result>>8)))
    registers[8:10]=initial[8:10];m1+=cost(0x6D06,0x6D38)
    registers[12],registers[15],registers[24]=stack+2,refresh(initial[15],m1),return_address
    return dict(registers=registers,writes=writes,refresh_m1=m1,overflow=overflow)
