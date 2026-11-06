"""6268, два независимых байтовых шага с различными условиями уменьшения и пропуска."""
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags,refresh


def signed_magnitude(difference):return (-difference)&255 if difference&128 else difference


def apply_codes(registers,current0,current1,rate,return_address=0x3FFF):
    r=list(registers);pointer=r[8]*256+r[9];target0,target1=r[2:4];writes=[]
    difference0=(current0-target0)&255;difference1=(current1-target1)&255
    magnitude0,magnitude1=signed_magnitude(difference0),signed_magnitude(difference1)
    first_shift=0
    if magnitude0>=2:
        # Расчёт числа делений шага на два по разрядности, без повторения исходной петли RRA.
        first_shift=max(0,rate.bit_length()-magnitude0.bit_length())
        if rate>>first_shift>magnitude0:first_shift+=1
        step=rate>>first_shift
        movement=step if difference0&128 else (-step)&255
        writes.append((pointer+8,(current0+movement)&255))
        first_m1=21+5*first_shift+int(step==magnitude0)
    else:first_m1=9+2*int(bool(difference0&128))
    if magnitude1<rate:
        r[0:2]=[magnitude1,cp_flags(magnitude1,rate)];second_m1=10+2*int(bool(difference1&128));second_written=False
    else:
        movement=rate if difference1&128 else (-rate)&255
        result=(current1+movement)&255;r[0:2]=[result,add_flags(movement,current1)]
        writes.append((pointer+9,result));second_m1=23+int(rate<magnitude1);second_written=True
    r[4:8]=[current1,difference1,magnitude1,magnitude0]
    r[12]+=2;r[24]=return_address;r[15]=refresh(r[15],first_m1+second_m1)
    return dict(registers=r,writes=writes,refresh_m1=first_m1+second_m1,
        differences=(difference0,difference1),magnitudes=(magnitude0,magnitude1),
        first_shift=first_shift,first_written=magnitude0>=2,second_written=second_written)
