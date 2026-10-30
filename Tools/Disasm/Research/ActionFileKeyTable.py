"""Исходный физический ключ ACTION из копируемого перехода станции."""
PATH='Source/StationExit/Data/ActionFileName.asm'


def render(source):
 raw=source[0x21B4:0x21BD]
 if raw!=b'ACTION  C':raise ValueError('Не подтверждено исходное имя ACTION')
 line=('Entry:'.ljust(16)+'FTrDosFileKey { { "ACTION  " }, #43 }').ljust(80)+'; Name из восьми байтов, Extension=C, терминатора нет'
 text='\n'.join(['                module ActionFileName','; Документация [выход станции](../../../Docs/StationExit.md)',
  '                assert $ == #4248',line,'                assert $ == #4251','                endmodule'])+'\n'
 return text,{'ActionFileName.Entry':0x4248,'ActionFileName.Entry.Name':0x4248,'ActionFileName.Entry.Extension':0x4250}
