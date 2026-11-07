"""EB41, две перспективы, коды пары и исходная XOR-ломаная B2,00,05,00."""
from ReferenceActionRecordFilters import Machine
from ReferenceActionOverlayProjection import evaluate as project
from ReferenceActionProjectedPairCodes import evaluate as codes
from ReferenceActionPacketRenderer import PacketRenderer
from CheckActionVertexCodes import logic_flags


class OverlayPairMachine(Machine):
    def exx(self):self.r[2:8],self.r[18:24]=self.r[18:24],self.r[2:8]

    def projection(self,return_address):
        child=project(self.r,return_address)
        for address,value in child['writes']:self.put(address,value)
        self.r=child['registers'];self.path.append(child['path'])

    def overlay_pair(self,ops):
        self.rendered=False
        self.call(0xADC5,0xEB44,lambda:self.projection(0xEB44));self.m1(1)
        if not self.r[1]&64:self.path.append('first_projection_rejected');return self.finish()
        self.put_word(0x8E00,self.r[6]*256+self.r[7]);self.put_word(0x8E02,self.r[4]*256+self.r[5]);self.exx();self.m1(4)
        self.call(0xADC5,0xEB50,lambda:self.projection(0xEB50));self.m1(1)
        if not self.r[1]&64:self.path.append('second_projection_rejected');return self.finish()
        self.put_word(0x8E05,self.r[6]*256+self.r[7]);self.put_word(0x8E07,self.r[4]*256+self.r[5]);self.exx();self.m1(4)
        self.m1(1);self.r[12]-=2;self.put_word(self.r[12],0xEB5C)
        child=codes(self.r,tuple((self.word(a),self.word(a+2)) for a in (0x8E00,0x8E05)),0xEB5C)
        for address,value in child['writes']:self.put(address,value)
        self.r=child['registers'];self.m1(1)
        if self.r[1]&64:self.path.append('both_codes_zero');return self.finish()
        aggregate=self.r[0];self.r[2]=aggregate;outside=(~aggregate)&240
        self.r[0:2]=[outside,logic_flags(outside)|16];self.m1(4)
        if outside:self.path.append('common_outside_side');return self.finish()
        low=aggregate&15;self.r[0:2]=[low,logic_flags(low)|16];self.pair(6,0xEB6E);self.m1(4+int(low==0))
        self.r[24]=0xDBBD if low else 0xDD23
        renderer=PacketRenderer(self.banks,self.r,ops,24,12);renderer.render(clipped=bool(low))
        self.r=renderer.r;self.banks=renderer.banks;self.writes.extend(renderer.writes)
        self.rendered=True;self.path.append('clipped_line' if low else 'inside_line')
        return self
