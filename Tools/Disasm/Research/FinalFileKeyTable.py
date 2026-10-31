"""Физические девять байтов имени FINALF в копии финального перехода."""
PATH='Source/StationFinalExit/Data/FinalFileName.asm'


def render(source):
 raw=source[0x1119:0x1122]
 if raw!=b'FINALF  C':raise ValueError('Не подтверждено исходное имя FINALF')
 line=('Entry:'.ljust(16)+'FTrDosFileKey { { "FINALF  " }, #43 }').ljust(80)+'; Name восемь байтов, Extension=C, терминатора нет'
 text='\n'.join(['                module FinalFileName','                ; Документация [финальный переход](../../../Docs/FinalExit.md)',
  '                assert $ == #405C',line,'                assert $ == #4065','                endmodule'])+'\n'
 return text,{'FinalFileName.Entry':0x405C,'FinalFileName.Entry.Name':0x405C,'FinalFileName.Entry.Extension':0x4064}
