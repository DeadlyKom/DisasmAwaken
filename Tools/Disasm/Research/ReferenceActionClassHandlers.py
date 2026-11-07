"""Числовые правила восьми классов, составленные с уже проверенными договорами потоков и фильтров."""
from ReferenceActionRecordFilters import Machine
from ReferenceControlsPointRespawn import cp_flags
from ReferenceControlsBcdExact import or_flags

ENTRIES={1:0x6594,2:0x6549,3:0x65DE,4:0x65AD,5:0x6525,6:0x657F,7:0x6566,8:0x6536}


class ClassMachine(Machine):
    def pointer(self):return self.r[8]*256+self.r[9]

    def override_gate(self,return_address):
        self.call(0x662B,return_address,self.override);self.m1(1)
        if not self.r[1]&64:
            self.path.append('parent_override_return');self.finish();return True
        return False

    def state(self,value):self.put(self.pointer()+10,value);self.m1(2)

    def filtered_result(self,entry,return_address):
        self.call(entry,return_address,lambda:self.filtered(entry));self.m1(1)
        if self.r[1]&64:self.path.append('parent_filter_Z');return self.finish()
        self.put(self.pointer()+11,self.r[0]);self.path.append('parent_filter_link');return self.finish(3)

    def class2_tail(self):
        if self.override_gate(0x655D):return self
        return self.filtered_result(0xE729,0x6561)

    def random_predicate(self,return_address,use_r):
        self.call(0xEB72,return_address,lambda:self.stream(0))
        # Логический результат считается прямо из нового слова и реально прочитанного R.
        if use_r:
            self.m1(2);value=(self.r[15]&self.r[6])|self.r[7];self.m1(3)
        else:
            value=self.r[6]|self.r[7];self.m1(3)
        self.r[0:2]=[value,or_flags(value)]
        self.path.append('predicate_nonzero' if value else 'predicate_zero')
        return value

    def r_link_start(self,threshold=112):
        self.m1(2);value=self.r[15];self.r[0:2]=[value,cp_flags(value,threshold)];self.m1(1)
        self.state(2);self.put(self.pointer()+11,255);self.m1(3)
        return value<threshold

    def handle(self,kind):
        entry=ENTRIES[kind]
        if self.override_gate(entry+3):return self
        if kind in (1,5,6,8):
            self.state(18 if kind==8 else 1)
            value=self.random_predicate({1:0x659F,5:0x6530,6:0x658A,8:0x6541}[kind],kind!=5)
            if kind==6:
                if value:self.path.append('class6_nonzero_common');return self.common_class_link()
                self.m1(1);self.path.append('class6_zero_secondary');return self.class2_tail()
            if value:return self.finish()
            if kind in (5,8):
                self.m1(1);return self.common_class_link()
            self.call(0x661A,0x65A7,self.common_class_link);self.m1(1)
            if self.r[1]&64:self.path.append('class1_common_Z');return self.finish()
            self.put(self.pointer()+18,0);self.path.append('class1_becomes_class0');return self.finish(3)
        below=self.r_link_start(self.read(0x65E5) if kind==3 else 112)
        if kind==3:
            if not below:return self.filtered_result(0xE745,0x65F3)
            gate=self.read(0x9BCD);self.r[0:2]=[gate,cp_flags(gate,64)];self.m1(3)
            if gate<64:self.path.append('class3_gate_below64');return self.finish()
            self.r[12]-=2;self.put_word(self.r[12],self.r[0]*256+self.r[1]);self.m1(1)
            self.call(0xEBA3,0x6602,lambda:self.stream(8))
            saved=self.word(self.r[12]);self.r[12]+=2;self.r[0:2]=[saved>>8,saved&255];self.m1(1)
            low=self.r[7];self.r[1]=cp_flags(gate,low);self.m1(2)
            if gate<low:self.path.append('class3_gate_below_low');return self.finish()
            high=self.r[6];self.r[0:2]=[high,cp_flags(high,3)];self.m1(3)
            if high>=3:self.path.append('class3_high_at_least3');return self.finish()
            self.put(self.pointer()+11,26);self.path.append('class3_code26');return self.finish(3)
        if below:self.path.append('parent_R_below112');return self.finish()
        if kind==2:return self.class2_tail()
        return self.filtered_result(0xE70D if kind==7 else 0xE745,0x657A if kind==7 else 0x65C1)
