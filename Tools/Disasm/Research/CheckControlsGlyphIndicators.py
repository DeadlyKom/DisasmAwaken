"""Полный E021 с настоящими рисователями, 64 очищаемых байта и все ветви координат."""
from collections import Counter
import sys
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsGlyphIndicators import reference


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    routes = Counter()
    glyphs = 0
    report_path = ROOT/"Tools/Disasm/Reports/ControlsGlyphIndicatorsVerification.json"
    prior = json.loads(report_path.read_text("utf-8")) if "--supplement" in sys.argv else None
    if prior is not None:
        assert prior["passed"] and prior["total_cases"] == 197688 and "supplement_cases" not in prior
    fill = [0x4000|((y&0xC0)<<5)|((y&7)<<8)|((y&0x38)<<2)|column
            for y in range(104,120) for column in range(19,25)]

    def check(mode,gate,first,second,third,background,kind,registers=None):
        nonlocal touched,glyphs
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        for address in fill:
            memory[address] = (background+73*address)&255
        memory[0x9B81:0x9B8D] = [mode,gate,background,third[1],third[0],third[2],*second,*first]
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        values = {'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE021}
        if registers is not None:
            assert set(registers)<=set(('HL','DE','BC','AF'))
            values.update(registers)
        initial = get_registers(values,None,False)
        initial[14],initial[15],initial[26],initial[27] = background,(background+mode+gate)&255,background&1,background%3
        expected = list(memory)
        wanted,writes,cost,route,count = reference(expected,initial,mode,gate,first,second,third)
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],cost)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(500):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',mode,gate,first,second,third))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (mode,gate,first,second,third,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (mode,gate,first,second,third,
            [(i,a,b) for i,(a,b) in enumerate(zip(memory,expected)) if a!=b][:8])
        touched = {address for address,_ in writes}
        counts[kind] += 1
        routes[route] += 1
        glyphs += count

    if prior is None:
        # Проверка каждой пары X,Y каждого из трёх входов, включая байтовые переполнения и границы ограничений.
        for selected in range(3):
            for y in range(256):
                for x in range(256):
                    vectors = [(0,0,0),(0,0,0),(0,0,0)]
                    vectors[selected] = (x,y,(x^y)&128)
                    check(0,0,*vectors,(31*x+17*y+selected)&255,'all_coordinates_'+str(selected))
                if y%64==63:
                    print('Glyph indicator',selected,'Y',y+1,'complete',flush=True)
        # Проверка каждого полного управляющего байта режима и запрета третьего знака.
        for value in range(256):
            check(value,value,(value,255-value,value),(255-value,value,value^128),(value, value^0x80,value),value,'all_mode_gate_values')
        # Проверка всех семи вариантов точного OR-маркера 80, обоих режимов и запрета третьего знака.
        for bits in range(1,8):
            vector = tuple(0x80 if bits&(1<<i) else 0 for i in range(3))
            for mode in (0,1):
                for gate in (0,255):
                    for sign in (0,128):
                        check(mode,gate,(0,0,sign),vector,(0,0,sign),bits*31,'all_sentinel_vectors')
        # Проверка каждого знакового байта в каждом входе без изменения прочих разрядов и с перекрытием знаков.
        for selected in range(3):
            for value in range(256):
                vectors = [(0,0,0),(0,0,0),(0,0,0)]
                vectors[selected] = (0,0,value)
                check(0,0,*vectors,value,'all_shape_sign_bytes')
    # Проверка сочетаний пропуска первого, допуска третьего и перекрытия плюса с квадратом.
    for bits in range(8):
        for index,(x,y) in enumerate(((0,0),(5,255),(255,254),(96,128))):
            vectors=[(x,y,0x81 if bits&(1<<i) else 0) for i in range(3)]
            for mode in (0,1):
                for gate in (0,1):
                    check(mode,gate,*vectors,(31*bits+index)&255,'branch_combinations')
    # Проверка исходных DE и B на пути без единого знака, где они должны сохраниться.
    for de in (0,1,255,256,0x7FFF,0x8000,0xFFFE,0xFFFF):
        for bc in (0,1,255,256,0x7FFF,0x8000,0xFF00,0xFFFF):
            check(1,0,(0,0,0),(128,0,0),(0,0,0),(de+bc)&255,'no_glyph_passthrough',
                  dict(DE=de,BC=bc,HL=de^bc,AF=de^bc))
    supplement = counts['branch_combinations']+counts['no_glyph_passthrough']
    assert supplement==192
    if prior is not None:
        counts.update(prior['cases_by_kind'])
        routes.update(prior['routes'])
        glyphs+=prior['glyphs_drawn']
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),routes=dict(routes),
        glyphs_drawn=glyphs,supplement_cases=supplement,first_skipped_third_drawn_checked=True,
        no_glyph_de_and_b_passthrough_checked=True,all_coordinates_of_each_input=True,all_mode_and_gate_byte_values=True,
        exact_or_sentinel_seven_vectors=True,all_sign_bytes_each_input=True,
        original_helpers_without_stubs=True,independent_coordinate_and_pixel_reference=True,
        clear_bytes=64,preserved_gap_columns=[21,24],temporary_sp_and_self_modified_restore_checked=True,
        byte_overflow_coordinate_quirks_preserved=True,exact_registers_flags_r_and_sp=True,
        every_ram_byte_and_write_checked=True,all_combined_vectors_exhausted=False,
        game_vector_meaning_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsGlyphIndicatorsVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
