"""Только стоимость M1 квадрата C6F4 для поддиапазона геометрии, не произвольного произведения."""
def refresh_cost(word):
    assert 0<=word<=65535 and word!=0x8000
    signed=word if word<32768 else word-65536;magnitude=abs(signed);sign_cost=14*int(signed<0)
    if magnitude==0:return 46
    if magnitude<256:
        trailing=(magnitude&-magnitude).bit_length()-1
        return 55-trailing+magnitude.bit_count()+sign_cost
    top=magnitude.bit_length()-1
    return 56+3*top+4*magnitude.bit_count()+sign_cost
