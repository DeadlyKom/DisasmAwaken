"""6F55, падающий фронт общего запроса, задержанные запреты каналов и фазовое затухание."""
from ReferenceActionRecordFilters import Machine
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsBufferPoints import sub8_flags
from CheckActionRecordIndex import add_flags

CHANNELS=((0x6F7B,0x6F7E,0x6F8D,0x9B96,0x7736,0x7713,200),
    (0x6FB0,0x6FB3,0x6FC2,0x9B95,0x7759,0x777C,200),
    (0x6FE5,0x6FE8,0x6FF6,0x9B97,0x76CD,0x76F0,250))


def release_class14(m):
    while True:
        m.r[4]=20;m.m1(1);m.call(0xE98D,0x6177,m.find_code);m.m1(1)
        if m.r[1]&64:return m.finish()
        def mark():
            pointer=m.r[10]*256+m.r[11]
            m.put(pointer+1,128);m.put(pointer,0);m.put(pointer+24,255);m.finish(7)
        m.call(0xF03D,0x617B,mark);m.m1(1)


def evaluate(banks,registers):
    m=Machine(banks,registers);current,previous=m.read(0x6F56),m.read(0x6F59)
    m.r[3]=previous;m.put(0x6F59,current);m.m1(5);released=current==0 and previous!=0
    # Проверка падающего фронта общего запроса, только он запускает освобождение класса 14.
    if current==0:
        m.m1(2)
        if released:
            m.call(0x6172,0x6F65,lambda:release_class14(m));m.pair(6,0x88)
            m.put_word(0x7693,0x88);m.put_word(0xA78F,0x88);m.put(0x669F,1);m.m1(6)
    m.r[0:2]=[0,0x44];m.put(0x6F56,0);m.m1(2);paths=[]
    for index,(old_address,new_address,phase_address,value_address,default0,default1,default) in enumerate(CHANNELS):
        old,new=m.read(old_address),m.read(new_address);m.put(old_address,new)
        m.r[0:2]=[new,logical_flags(old)];m.m1(5)
        if old:paths.append('latched_skip');continue
        # Обновление двух исходных операндов клавиатурных обработчиков и кольцевой фазы.
        phase=m.read(phase_address);rotated=(phase>>1)|((phase&1)<<7)
        m.put(default0,default);m.put(default1,default);m.put(phase_address,rotated)
        m.r[0:2]=[rotated,0x44|(rotated&0x28)|(phase&1)];m.m1(7)
        if not phase&1:paths.append('even_phase_skip');continue
        value=m.read(value_address);m.r[0:2]=[value,logical_flags(value)|16];m.m1(3)
        if value==0:paths.append('zero_skip');continue
        # Расчёт одного шага signed8 к нулю, переход FF в 00 использует исходный XOR.
        if value<128:result=value-1;flags=sub8_flags(value,1);cost=4
        elif value<255:result=value+1;flags=add_flags(value,1);cost=4
        else:result=0;flags=0x44;cost=6
        m.r[0:2]=[result,flags];m.put(value_address,result);m.m1(cost+int(index==2));paths.append('decayed')
    m.finish();return dict(machine=m,released=released,channels=paths)
