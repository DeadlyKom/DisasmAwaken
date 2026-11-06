"""7680 и 76A3, точные исходные условия слова шестой шкалы, без нормализующего насыщения."""
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import cp_flags,refresh
from ReferenceControlsBufferPoints import sub16_flags


def evaluate(registers,entry,request,opcode,word,limit):
    r=list(registers);writes=[];reason='';m1=0
    if entry==0x7680:
        r[0:2]=[request,logical_flags(request)];m1=3
        if request:reason='request_block'
        else:
            r[0:2]=[opcode,cp_flags(opcode,58)];m1+=3
            if opcode!=58:reason='opcode_block'
            else:
                candidate=(word+8)&65535;difference=(candidate-limit)&65535;flags=sub16_flags(candidate,limit)
                # Расчёт флагов исходного обратного ADD, знак остаётся от SBC, биты 3/5 уже от кандидата.
                flags=(flags&0xC4)|((candidate>>8)&0x28)|(16 if (difference&4095)+(limit&4095)>4095 else 0)|int(difference+limit>65535)
                r[4:8]=[limit>>8,limit&255,candidate>>8,candidate&255];r[1]=flags;m1+=9
                if flags&128:
                    writes.extend(((0xA78F,candidate&255),(0xA790,candidate>>8),(0x669F,1)))
                    r[0]=1;m1+=4;reason='word_written'
                else:reason='difference_sign_block'
    else:
        assert entry==0x76A3
        r[0:2]=[opcode,cp_flags(opcode,58)];m1=3
        if opcode!=58:reason='opcode_block'
        else:
            r[0:2]=[request,logical_flags(request)|16];m1+=3
            if request:reason='request_block'
            else:
                r[4:8]=[0,8,word>>8,word&255];m1+=5
                if word&32768:
                    m1+=3
                    if not word&16:r[1]=0x54|(word&0x28);reason='negative_bit4_block'
                if not reason:
                    result=(word-8)&65535;r[0:2]=[1,sub16_flags(word,8)];r[6:8]=[result>>8,result&255]
                    writes.extend(((0xA78F,result&255),(0xA790,result>>8),(0x669F,1)));m1+=7;reason='word_written'
    r[15]=refresh(r[15],m1);r[12]+=2;r[24]=0x3FFF
    return dict(registers=r,writes=writes,refresh_m1=m1,reason=reason)
