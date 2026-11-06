"""7EB7, копия трёх dword, исходное насыщение и настоящая композиция кодов движения."""
from ReferenceActionClampVectorWords import evaluate as clamp
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes


def evaluate(registers,values,record_words,currents,rate,ratio_table,root_table):
    r=list(registers);stack=r[12];writes=[]
    def put(address,word):writes.extend(((address,word&255),(address+1,word>>8)))
    # Обновление шести исходных операндов без переноса или выделения памяти.
    for (high,low),value in zip(((0x7F0F,0x7F12),(0x7F23,0x7F26),(0x7F37,0x7F3A)),values):
        put(high,value>>16);put(low,value&65535)
    put(stack-2,0x7EF3);child=list(r);child[12]=stack-2
    bounded=clamp(child,values,return_address=0x7EF3);writes.extend(bounded['writes'])
    r=bounded['registers'];first=r[6]*256+r[7];second=r[4]*256+r[5];third=r[2]*256+r[3]
    put(stack-2,third);put(stack-4,second)
    # Преобразование результатов POP/EXX в шесть аргументов известной геометрии.
    for index,word in ((6,first),(4,record_words[0]),(2,record_words[1]),(22,second),(20,third),(18,record_words[2])):
        r[index:index+2]=[word>>8,word&255]
    put(stack-2,0x6268);r[12]=stack-2;r[24]=0xAD5A
    delta=geometry(r,ratio_table,root_table,return_address=0x6268);writes.extend(delta['writes'])
    local=apply_codes(delta['registers'],*currents,rate);writes.extend(local['writes'])
    return dict(registers=local['registers'],writes=writes,ports=delta['ports'],clamped=(first,second,third),
        targets=tuple(delta['registers'][2:4]),deltas=delta['deltas'],root_input=delta['root_input'])
