"""E9C2, ближайший кандидат по квантованному максимуму, два изменяемых операнда."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionRecordFilters import Machine


class NearestMachine(Machine):
    def exx(self):
        self.r[2:8],self.r[18:24]=self.r[18:24],self.r[2:8]

    def index_address(self):
        value=self.r[0];pointer=0xA100+64*value
        self.pair(6,pointer);self.r[0:2]=[pointer>>8,add_flags(value>>2,0xA1)]
        return self.finish(12)

    def distance(self):
        ix=self.r[8]*256+self.r[9];iy=self.r[10]*256+self.r[11]
        delta=[(self.word(iy+2*k)-self.word(ix+2*k))&65535 for k in range(3)]
        mag=[(-v)&65535 if v&32768 else v for v in delta];a,b,c=[v>>8 for v in mag]
        stack=self.r[12];self.put_word(stack-2,mag[0]);self.put_word(stack-4,mag[1])
        self.pair(6,mag[2]);self.pair(4,mag[0]);self.r[0:2]=[max(a,b,c),cp_flags(max(b,c),a)]
        return self.finish(45+7*sum(bool(v&32768) for v in delta)+int(c<b)+2*int(a>max(b,c)))

    def nearest(self):
        cursor=0xA01C;self.put(0xE9E7,255);self.m1(3)
        for _ in range(1024):
            value=self.read(cursor);self.pair(6,cursor);self.r[0:2]=[value,cp_flags(value,254)];self.m1(4)
            if value==254:
                self.r[0]=self.read(0xE9FE);self.path.append('end');return self.finish(2)
            self.m1(2)
            if value==255:cursor+=1;self.path.append('skip');continue
            self.r[0]=value;self.exx();self.m1(2)
            self.call(0xE6A7,0xE9D9,self.index_address)
            pointer=self.r[6]*256+self.r[7];self.r[7]=(self.r[7]+1)&255
            high=self.read(pointer+1);self.r[0:2]=[high,cp_flags(high,128)];self.m1(4)
            if high==128:
                self.exx();self.put(cursor,255);self.m1(3);self.path.append('invalidate');cursor+=1;continue
            self.pair(6,pointer);self.pair(10,pointer)
            self.put_word(self.r[12]-2,pointer);self.m1(4)
            self.call(0xEAE9,0xE9E6,self.distance)
            distance=self.r[0];limit=self.read(0xE9E7)
            self.r[1]=cp_flags(distance,limit);self.m1(2)
            if distance<limit:
                self.put(0xE9E7,distance);self.put(0xE9FE,self.read(cursor));self.r[0]=self.read(cursor)
                self.m1(5);self.path.append('improve')
            else:self.path.append('tie_or_farther')
            self.exx();self.m1(2);cursor+=1
        raise AssertionError('список не достиг FE, это защитный предел модели')


def profiles():
    # Проверка полного диапазона разности одной компоненты, остальные компоненты равны нулю.
    for delta in range(65536):yield (1,254),((0,0,0),(delta,0,0)),delta&255,'all_first_differences'
    # Проверка всех обычных кодов списка, за исходным массивом читаются оригинальные байты.
    for index in range(254):
        for unavailable in (False,True):
            yield (index,254),((0,0,0),(511,256,0)),index,'all_indices_unavailable' if unavailable else 'all_indices'
    edges=(0,1,255,256,511,512,32767,32768,65535)
    for a in edges:
        for b in edges:
            for c in edges:yield (255,1,2,1,254),((0,0,0),(a,0,0),(b,c,0)),a&255,'ties_and_boundaries'
    for old in range(256):
        yield (254,),((0,0,0),),old,'empty_stale'
        yield (255,255,254),((0,0,0),),old,'skipped_stale'
        yield (1,1,254),((0,0,0),(0,0,0)),old,'duplicate_unavailable'
    # Проверка разных источников окончательных A, IY, HL' и DE'.
    records=((0,0,0),(1,0,0),(512,256,768),(32768,0,0))
    yield (1,2,254),records,126,'last_available_is_not_best'
    yield (1,2,3,254),records,126,'unavailable_after_available'
    yield (3,254),records,126,'only_unavailable_context'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;counts=Counter();paths=Counter();max_stack=0;costs=set()
    for items,records,old,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for index,values in enumerate(records):
            pointer=0xA100+64*index
            for axis,value in enumerate(values):memory[pointer+2*axis],memory[pointer+2*axis+1]=value&255,value>>8
        if profile=='all_indices_unavailable' and items[0]<26:memory[0xA101+64*items[0]]=128
        if profile=='duplicate_unavailable':memory[0xA141]=128
        for index,value in enumerate(items):memory[0xA01C+index]=value
        memory[0xE9FE]=old;memory[0xE9E7]=old^255
        stack=0x8002 if cases&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xE9C2,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        model=NearestMachine(memory.banks,initial);model.nearest()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        measured_m1=0
        for _ in range(2000):
            if simulator.registers[24]==0x3FFF:break
            previous_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-previous_r)&127
            assert increment in (1,2),(cases,'неожиданное изменение R',increment)
            measured_m1+=increment
        else:raise AssertionError(('нет возврата',profile,items))
        assert measured_m1==model.m1_count,(cases,'M1',measured_m1,model.m1_count)
        costs.add(measured_m1)
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM',model.path)
        # Проверка явно заданных контекстов, последний обработанный кандидат отличается от лучшего.
        def pair(index):return simulator.registers[index]*256+simulator.registers[index+1]
        if profile=='last_available_is_not_best':
            assert (simulator.registers[0],pair(10),pair(22),pair(20))==(1,0xA180,768,512)
        elif profile=='unavailable_after_available':
            assert (simulator.registers[0],pair(10),pair(22),pair(20))==(1,0xA180,0xA1C1,512)
            assert memory[0xA01E]==255
        elif profile=='only_unavailable_context':
            assert (simulator.registers[0],pair(10),pair(22),pair(20))==(126,0x5C3A,0xA1C1,0x5678)
        max_stack=max(max_stack,max((stack-(offset+(0x4000 if bank==5 else 0x8000)) for bank,offset,_ in memory.writes if bank in (2,5) and stack-8<=offset+(0x4000 if bank==5 else 0x8000)<stack),default=0))
        paths.update(model.path);counts[profile]+=1;cases+=1
        if cases%32768==0:print(str(cases)+' nearest candidate cases passed',flush=True)
    assert cases==67544 and max_stack==6 and paths['invalidate'] and paths['tie_or_farther']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),stack_bytes=max_stack,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_index_and_distance_children_executed=True,all_254_ordinary_index_bytes=True,
        no_valid_candidate_preserves_old_result_operand=True,first_equal_distance_wins=True,
        full_M1_count_compared_not_only_R_modulo_128=True,observed_M1_min=min(costs),observed_M1_max=max(costs),
        explicit_last_available_not_best_and_mixed_alternate_context_cases=3,
        all_possible_lists_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionNearestCandidateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
