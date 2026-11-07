"""617D, числовая композиция поиска, потока 8 и транспонированной матрицы."""
from ReferenceActionChildSpawn import SpawnMachine
from ReferenceActionPatchedVector import evaluate
from CheckActionPatchedVector import INPUTS,COEFFICIENTS,OUTPUTS
from CheckActionPatchSwap import PAIRS


class Class20Machine(SpawnMachine):
    def transposed(self):
        vector=[self.r[i]*256+self.r[i+1] for i in (6,4,2)]
        matrix=[[self.read(p) for p in row] for row in COEFFICIENTS]
        old=[self.word(p) for p in OUTPUTS];stack=self.r[12]
        ix=self.r[8]*256+self.r[9];iy=self.r[10]*256+self.r[11]
        self.put_word(stack-2,ix);self.put_word(stack-4,iy)
        for address,value in zip(INPUTS,vector):self.put_word(address,value)
        self.put_word(stack-6,0xACFC)
        # Перестановка именно физических слов с сохранением старших байтов префиксов.
        for left,right in PAIRS:
            a,b=self.word(left),self.word(right);self.put_word(right,a);self.put_word(left,b)
        self.put_word(0xAD08,stack-4);self.put_word(0xAFF1,ix)
        result=evaluate(vector,list(map(list,zip(*matrix))),old)
        for row in result['performed']:self.put_word(OUTPUTS[row],result['outputs'][row])
        self.put_word(stack-6,0xAD0D)
        for left,right in PAIRS:
            a,b=self.word(left),self.word(right);self.put_word(right,a);self.put_word(left,b)
        for i,value in zip((6,4,2),result['outputs']):self.pair(i,value)
        self.r[0:2]=result['af'];self.r[16:18]=result['alternate_af']
        self.path.append('transform_overflow' if result['overflow'] else 'transform_complete')
        return self.finish(result['refresh_m1']+65)

    def spawn20(self):
        self.call(0xE9A1,0x6180,self.reusable);self.m1(1)
        if self.r[1]&64:return self.finish()
        self.call(0xEBA3,0x6184,lambda:self.stream(8));high,low=self.r[6:8]
        # Преобразование двух знаковых байтов в компоненты с отступом от нуля.
        def component(value):
            signed=value-256 if value&128 else value
            return (signed*4+(-1024 if signed<0 else 1024))&65535
        self.pair(6,component(low));self.pair(4,component(high))
        mode=self.read(0x6E75);self.pair(2,30000 if mode==0 else 35536)
        self.m1(35+int(low>=128)+int(high>=128)+int(mode!=0))
        self.call(0xACEA,0x61BC,self.transposed)
        iy=self.r[10]*256+self.r[11]
        for offset,index in ((0,6),(2,4),(4,2)):
            self.put_word(iy+offset,self.r[index]*256+self.r[index+1])
        for field,value in ((7,12),(8,29),(9,55),(6,192),(18,20),(19,250),(10,4),
                            (24,0),(12,0),(36,0),(37,2),(16,2),(15,2)):
            self.put(iy+field,value)
        self.r[0:2]=[0,0x44];self.path.append('class20_created')
        return self.finish(40)
