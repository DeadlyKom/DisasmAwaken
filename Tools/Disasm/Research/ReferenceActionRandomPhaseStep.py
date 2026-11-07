"""6201, отдельный поток 0, знаковый таймер и шаг третьей фазы с отражением направления."""
from ReferenceActionRecordFilters import Machine
from CheckActionMissileConsume import dec_flags
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import cp_flags


class RandomPhaseMachine(Machine):
    def random_phase(self):
        ix=self.r[8]*256+self.r[9]
        self.call(0xEB72,0x6204,lambda:self.stream(0));high,low=self.r[6:8];self.m1(3)
        if high==127:
            self.m1(4)
            if low&127>=16:
                magnitude=(low&15)+32;self.r[6]=magnitude
                self.put(ix+23,magnitude|(low&128));self.m1(8);self.path.append('random_timer_reset')
        timer=self.read(ix+23);low_timer=timer&127;value=(low_timer-1)&255
        self.r[0:2]=[value,dec_flags(low_timer,0)];self.m1(5)
        if low_timer==0:self.path.append('phase_idle');return self.finish()
        timer=(timer-1)&255;self.put(ix+23,timer);negative=bool(timer&128)
        phase=(self.read(ix+9)+(-1 if negative else 1))&255;self.put(ix+9,phase)
        magnitude=(-phase)&255 if phase&128 else phase
        self.r[0:2]=[magnitude,cp_flags(magnitude,64)]
        self.m1(14+int(negative)+2*int(bool(phase&128)))
        if magnitude<64:self.path.append('phase_inside');return self.finish()
        timer^=128;self.put(ix+23,timer);self.r[0:2]=[timer,logic_flags(timer)]
        self.path.append('phase_direction_flipped');return self.finish(6)
