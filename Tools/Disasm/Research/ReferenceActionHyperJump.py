"""70F6..7175, списание выбранного байта до сравнения и переноса пятибайтового контекста."""
from ReferenceActionRecordFilters import Machine
from CheckControlsEvenSpan import and_flags
from CheckActionRecordSearch import inc_flags
from ReferenceControlsBufferPoints import sub16_flags,sub8_flags


class HyperJumpMachine(Machine):
    def request(self):
        delay=self.read(0xA85F);self.r[:2]=[delay,and_flags(delay)]
        if delay:self.path.append('delay');return self.finish()
        equipment=self.read(0x9C26);self.r[:2]=[(equipment+1)&255,inc_flags(equipment,0)]
        if equipment==255:self.path.append('no_hypertrail');return self.finish()
        preferred=self.read(0x9C10);address=0x9C10 if preferred else 0x9C11
        cost=self.read(0x9C8A)*(2 if preferred else 1);value=self.read(address);difference=(value-cost)&65535
        self.pair(6,difference);self.pair(4,cost);self.r[:2]=[0,sub16_flags(value,cost)]
        if value<cost:self.path.append('insufficient_selected_byte');return self.finish()
        self.r[0]=difference&255;self.put(address,difference&255)
        # Проверка равенства идёт после необратимого расхода, два слова и последний байт сравниваются последовательно.
        destination=[self.read(0x9BC6+i) for i in range(5)];current=[self.read(0x9BC1+i) for i in range(5)]
        differs=False
        for offset in (0,2):
            left=destination[offset]+256*destination[offset+1];right=current[offset]+256*current[offset+1]
            self.pair(6,(left-right)&65535);self.pair(4,right);self.r[:2]=[0,sub16_flags(left,right)]
            if left!=right:differs=True;break
        if not differs:
            self.r[2]=current[4];self.r[:2]=[(destination[4]-current[4])&255,sub8_flags(destination[4],current[4])]
            if destination[4]==current[4]:self.path.append('same_context_after_spend');return self.finish()
        for i,value in enumerate(destination):self.put(0x9BC1+i,value)
        self.pair(6,destination[2]+256*destination[3]);self.r[0]=destination[4];self.r[24]=0x7176
        self.path.append('accepted_before_message');return self
