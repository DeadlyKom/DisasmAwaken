"""Линейная заливка D511 против геометрических строк и исходных предвычисленных масок."""
from collections import Counter
import inspect,json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckPreviewPolygon import hull
import PreviewPolygonOracle as reference
from ReferenceControlsPointRespawn import cp_flags
from ActionPolygonFillOracle import registers
from PreviewEdgeRasterOracle import arithmetic
from ReferenceActionPolygonFill import fill


def main():
    flat=flat_action();patterns=tuple((flat[0xD100+2*i],flat[0xD101+2*i]) for i in range(5))
    assert patterns==reference.PATTERNS[:5]
    # Проверка 320 действительно используемых байтов масок, промежутки не перезаписываются и не объявляются мусором.
    mask_addresses=[]
    for parity in range(2):
        for phase in range(8):
            for mode,(first,delta) in enumerate(patterns):
                pattern=first^(delta if parity else 0)
                for right in (False,True):
                    address=0x8C00+parity*256+phase*32+mode*2+(16 if right else 0)
                    preserve=(255>>phase) if right else ((255<<(8-phase))&255)
                    assert flat[address:address+2]==[preserve,pattern&~preserve]
                    mask_addresses.extend((address,address+1))
    namespace=dict(reference.raster.__globals__)
    namespace['address']=lambda row,column:0x8000+row*32+column//8
    text=inspect.getsource(reference.raster).replace('-0x4000','-0x8000')
    exec(compile(text,'<action_linear_polygon_bitmap>','exec'),namespace);raster=namespace['raster']
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);s=Simulator(m);counts=Counter();unchanged_outside=0
    def check(vertices,mode):
        nonlocal unchanged_outside
        m.recording=False
        for bank in (0,2):m.banks[bank][:]=base[bank]
        serial=counts.total()
        source=(bytes(3072),bytes([255])*3072,bytes((i*37+11)&255 for i in range(3072)),bytes((85,170))*1536)[serial%4]
        wanted=raster(source,vertices,mode)
        m.banks[2][:3072]=source
        for i,(row,column) in enumerate(vertices):m[0x9000+2*i],m[0x9001+2*i]=column,row
        m[0x9BA3]=2*len(vertices);m[0xD560]=mode;m[0xBFFE],m[0xBFFF]=255,63
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xD511},None,False)
        before=[bytearray(b) for b in m.banks]
        expected_ram,expected_writes=fill(before,vertices,mode)
        s.registers[:]=initial;m.writes=[];m.recording=True
        for _ in range(100000):
            if s.registers[PC]==0x3FFF:break
            s.run()
        else:raise AssertionError(('возврат заливки',vertices,mode))
        m.recording=False
        assert bytes(m.banks[2][:3072])==wanted,(vertices,mode,'bitmap')
        # Проверка всех физических банков и кратности записей по общему целочисленному эталону.
        assert all(a==b for a,b in zip(expected_ram,m.banks)),(vertices,mode,'whole RAM')
        assert Counter(expected_writes)==Counter(m.writes),(vertices,mode,'whole writes',Counter(expected_writes)-Counter(m.writes),Counter(m.writes)-Counter(expected_writes))
        assert all(m[a]==flat[a] for a in mask_addresses),(vertices,mode,'mask table')
        low,high=min(y for y,x in vertices),max(y for y,x in vertices)
        assert s.registers[SP]==0xC000 and s.registers[6:8]==initial[6:8]
        assert s.registers[0:2]==[high,cp_flags(high,high)]
        # Проверка конечных регистров по геометрии двух цепочек и переносу линейного адреса.
        r=s.registers;out=registers(vertices,mode)
        assert tuple(r[:2])==out['af'] and r[2]*256+r[3]==out['bc'] and r[4]*256+r[5]==out['de'],(vertices,mode,r[:8],out)
        if out['degenerate']:
            assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
            value,flags=arithmetic(len(vertices)*2,1,True)
            assert tuple(r[16:18])==(value,(flags&254)|(initial[1]&1))
        else:
            assert (r[8]*256+r[9],r[10]*256+r[11])==(out['ix'],out['iy']),(vertices,mode,r[8:12],out)
            assert tuple(r[16:18])==out['alt_af'] and r[18]*256+r[19]==out['alt_bc'] and r[20]*256+r[21]==out['alt_de'] and r[22]*256+r[23]==out['alt_hl'],(vertices,mode,r[16:24],out)
        for bank,index,value in m.writes:
            address=(0x8000 if bank==2 else 0xC000 if bank==0 else 0x4000)+index
            allowed=(bank==2 and (index<3072 or 0x3FFC<=index<0x3FFE)) or (bank==0 and (0xD194<=address<0xD5C9 or 0xFFD0<=address<0xFFE0))
            if not allowed:
                assert value==before[bank][index],(vertices,mode,'outside changed write',hex(address),value,before[bank][index])
                unchanged_outside+=1
        counts['flat' if low==high else 'filled']+=1
    # Проверка размеров полос, треугольников и пяти оригинальных шаблонов.
    for height in range(1,17):
        for width in range(1,33):
            for mode in range(5):
                check(((3,5),(3,5+width),(3+height,5+width),(3+height,5)),mode)
                check(((3,5),(3+height,5+width),(3+height,5)),mode)
                check(((3,5+width),(3+height,5+width),(3+height,5)),mode)
    # Проверка общего выхода без строк заливки.
    for row in range(96):
        for mode in range(5):check(((row,3),(row,19),(row,37)),mode)
    # Проверка длин до максимума 60 точек после исходного ClipPolygon, включая повторённые вершины.
    for count in range(3,61):
        vertices=[(2,3),(93,245),(93,3)] if count==3 else [(2,3)]*(count-3)+[(2,245),(93,245),(93,3)]
        for mode in range(5):check(vertices,mode)
    rng=random.Random(0xD511)
    # Проверка исходного переноса адреса при схлопывании узкого контура у последней колонки.
    for height in (2,3,8,16,31,64,94,95):
        for mode in range(5):check(((0,254),(0,255),(height,255)),mode)
    for _ in range(1024):
        vertices=hull([(rng.randrange(96),rng.randrange(256)) for _ in range(rng.randrange(4,20))])
        if len(vertices)<3:continue
        for rotation in (0,1,len(vertices)-1):
            check(vertices[rotation:]+vertices[:rotation],rng.randrange(5))
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),original_patterns=patterns,mask_bytes_verified=320,
        linear_buffer_256_by_96=True,bitmap_exact=True,lower_scanline_excluded=True,
        restored_HL_and_SP_and_final_AF_checked=True,all_main_alternate_and_index_registers_proved=True,
        refresh_register_and_timing_proved=False,all_final_registers_proved=False,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,outside_unchanged_write_attempts=unchanged_outside,
        actual_source_instructions_without_stubs=True,convex_positive_winding_profile=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonFillBitmapVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
