"""EA77, независимый подсчёт R и побочных эффектов игрового дочернего списка."""
from CheckActionRecordIndex import add_flags
from CheckActionRecordSearch import inc_flags
from CheckActionMissileConsume import dec_flags
from CheckMarketAccess import add16_flags
from ReferenceControlsPointRespawn import cp_flags


def generate(model,rom):
    ix=model.r[8]*256+model.r[9];mask=model.read(0xEAC4)
    model.pair(6,0xA0C1);model.m1(3);count=(model.r[15]&3)+2
    model.r[0:2]=[count,add_flags(count-2,2)];model.m1(2)
    model.path.append('children_requested_'+str(count));created=0
    while True:
        model.r[0:2],model.r[16:18]=model.r[16:18],model.r[0:2];model.pair(4,64);model.m1(2)
        while True:
            pointer=model.r[6]*256+model.r[7]+64;model.pair(6,pointer)
            high=model.read(pointer);model.r[0:2]=[high,cp_flags(high,128)];model.m1(4)
            if high==128:break
        pointer-=1;model.pair(6,pointer);low=model.read(pointer)
        model.r[0:2]=[low,cp_flags(low,128)];model.m1(4)
        if low==128:model.path.append('children_marker');break
        # Копирование шести физических байтов LDI сохраняет поведение при совпадении источника и слота.
        for k in range(6):model.put(pointer+k,model.read(ix+k))
        model.m1(17)
        for offset,value in ((6,184),(10,4),(12,0)):model.put(pointer+offset,value)
        model.m1(13);model.m1(2);sample=model.r[15]
        model.rom_samples=getattr(model,'rom_samples',[])+[sample,sample+1]
        model.put(pointer+13,rom[sample]);model.put(pointer+14,rom[sample+1]);model.m1(10)
        model.m1(2);kind=(model.r[15]&31)|mask;model.put(pointer+16,kind);model.m1(5)
        for offset,value in ((18,16),(19,16),(20,255),(21,255),(22,0)):model.put(pointer+offset,value)
        model.r[0:2]=[0,inc_flags((pointer+21)&255,0)];model.m1(12)
        model.pair(2,0xFFEB);model.pair(4,ix+6);model.pair(6,pointer+1)
        model.r[1]=add16_flags(pointer+22,0xFFEB,model.r[1]);model.m1(3)
        model.r[0:2],model.r[16:18]=model.r[16:18],model.r[0:2]
        old=model.r[0];model.r[0:2]=[(old-1)&255,dec_flags(old,model.r[1]&1)];model.m1(3)
        created+=1
        if not model.r[0]:break
    model.path.append('children_created_'+str(created))
