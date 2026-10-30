"""Исходный начальный LF и шестнадцать непустых префиксов имени системы."""
PATH='Source/Map/Data/SystemPrefixes.asm'
NAMES=('Alpha','Beta','Gamma','Delta','Epsilon','Zeta','Eta','Theta','Iota','Kappa','Lambda','Sigma','Omega','Xi','Pi','Psi')


def render(source):
 if source[0x2721]!=10:raise ValueError('Не подтверждён начальный LF таблицы')
 lines=['                module SystemPrefixes','; Документация [имя системы](../../../Docs/SystemName.md)',
  '                assert $ == #E721',('Entry:'.ljust(16)+'db #0A').ljust(80)+'; начальный LF, SkipLfRecords пропускает индекс плюс один ограничитель']
 symbols={'SystemPrefixes.Entry':0xE721};position=0x2722
 for name in NAMES:
  end=source.index(10,position)+1;raw=source[position:end]
  lines+=['                ; исходный префикс CP866 и LF, текст не нормализуется',
   (name+':').ljust(16)+'db '+', '.join('#'+format(value,'02X') for value in raw)]
  symbols['SystemPrefixes.'+name]=position+0xC000;position=end
 if position!=0x2779:raise ValueError('Не подтверждена граница шестнадцати префиксов')
 lines+=['                assert $ == #E779','                endmodule']
 return '\n'.join(lines)+'\n',symbols
