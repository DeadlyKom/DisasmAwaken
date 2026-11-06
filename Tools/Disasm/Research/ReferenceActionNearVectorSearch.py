"""69BE, первый близкий вектор и выбор по старшему байту средних слов с поздними равенствами."""
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import refresh,cp_flags
from ReferenceControlsBufferPoints import sub8_flags


def check_words(values):
    m1=0
    for value in values:
        word=value>>16;folded=word if word<0x8000 else word^65535;m1+=10+6*(word>=0x8000)
        high=folded>>8
        if high:return False,folded,high,logical_flags(high),m1
        m1+=3;low=folded&255;flags=cp_flags(low,60)
        if low>=60:return False,folded,low,flags,m1
    return True,folded,low,flags,m1


def evaluate(registers,rows):
    r=list(registers);count=len(rows);stack=r[12];writes=[]
    if count==0:
        r[0:2]=[0,0x44];r[7]=127;m1=4;found=None
    else:
        # Создание реальной рамки сохранённого IY и возвратов вызовов предиката.
        iy=r[10]*256+r[11];writes.extend(((stack-2,iy&255),(stack-1,iy>>8)))
        m1=10;found=None
        for index,values in enumerate(rows):
            accepted,folded,a,flags,child_m1=check_words(values)
            writes.extend(((stack-4,0xD2),(stack-3,0x69)))
            if accepted:found=index;m1+=2+child_m1;break
            m1+=5+child_m1
        if found is None:
            end=0x9B27+12*count;start=end-12
            flags=(flags&0xC4)|((end>>8)&0x28)|(16 if (start&4095)+12>4095 else 0)
            r[0:2]=[a,flags];r[2]=0;r[4:8]=[0,12,folded>>8,127];m1+=4
        else:
            # Выбор максимального только старшего байта, при равенстве побеждает более поздняя компонента.
            middle=[((v>>8)&65535)^(65535 if v&0x80000000 else 0) for v in values]
            selected=max(range(3),key=lambda i:(middle[i]>>8,i));word=middle[selected]
            replace1=(middle[1]>>8)>=(middle[0]>>8)
            replace2=(middle[2]>>8)>=max(middle[0]>>8,middle[1]>>8)
            m1+=35+6*sum(bool(v&0x80000000) for v in values)+2*replace1+2*replace2
            remaining=count-found;r[0:2]=[found,sub8_flags(count,remaining)];r[2]=remaining
            r[4:8]=[middle[2]>>8,found,word&255,word>>8]
    r[15]=refresh(r[15],m1);r[12]=stack+2;r[24]=0x3FFF
    return dict(registers=r,writes=writes,refresh_m1=m1,found_index=found)
