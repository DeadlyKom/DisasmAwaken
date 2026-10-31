"""Шестнадцать пар начальных индексов рынка, выбираемых числовым уровнем системы."""
PATH='Source/Station/Data/ModelAvailability.asm'
START=0x34BC
END=0x34DC
FIELDS=('ShipBase','SkimmerBase')


def render(source):
 raw=source[START:END];assert len(raw)==32;lines=['                module ModelAvailability','                ; Документация [доступность моделей по уровню](../../../Docs/ModelAvailability.md)','                assert $ == #94BC'];symbols={}
 for i in range(16):
  ship,skimmer=raw[2*i:2*i+2];assert ship<=5 and skimmer<=3;label='Level'+str(i+1).zfill(2);address=0x6000+START+2*i;symbols['ModelAvailability.'+label]=address
  for offset,field in enumerate(FIELDS):symbols['ModelAvailability.'+label+'.'+field]=address+offset
  line=(label+':').ljust(16)+'FModelAvailability { #'+format(ship,'02X')+', #'+format(skimmer,'02X')+' }';lines.append(line.ljust(80)+'; уровень '+str(i+1)+', ShipBase='+str(ship)+', SkimmerBase='+str(skimmer))
 lines+=['                assert $ == #94DC','                endmodule'];return '\n'.join(lines)+'\n',symbols


def name_operands(region,address,operation):
 if region=='Station' and address==0x67E0:operation=operation.replace('LD HL, #94BC','LD HL, @ModelAvailability.Level01')
 return operation
