"""Семь исходных LF-строк, шесть двухбайтовых порогов и подпись ранга."""
PATH='Source/Station/Data/PlayerRanks.asm'
TEXTS=((0xACE3,0xACEB,'Rookie'),(0xACEB,0xACF4,'Score10000'),(0xACF4,0xACFD,'Score3000'),
 (0xACFD,0xAD06,'Score1000'),(0xAD06,0xAD0F,'Score300'),(0xAD0F,0xAD17,'Score100'),(0xAD17,0xAD21,'Score30'))


def render(source):
 lines=['; Документация [ранги](../../../Docs/PlayerRank.md)','                module RankTexts','                assert $ == #ACE3'];symbols={}
 for begin,end,name in TEXTS:
  raw=source[begin-0x6000:end-0x6000]
  if raw[-1]!=10 or 10 in raw[:-1]:raise ValueError('Не подтверждена исходная LF-строка ранга')
  lines+=['                ; исходные байты CP866 и завершающий LF, содержимое строки сохранено',
   (name+':').ljust(16)+'db '+', '.join('#'+format(value,'02X') for value in raw)]
  symbols['RankTexts.'+name]=begin
 lines+=['                assert $ == #AD21','                endmodule','','                module RankThresholds']
 for i,score in enumerate((10000,3000,1000,300,100,30)):
  offset=0x4D21+2*i;raw=source[offset:offset+2]
  if int.from_bytes(raw,'big')!=score:raise ValueError('Изменён исходный порог ранга')
  name='Score'+str(score);line=((name+':').ljust(16)+'FRankThreshold { '+', '.join('#'+format(value,'02X') for value in raw)+' }').ljust(80)+'; HighByte, LowByte, порог '+str(score)
  lines.append(line);symbols['RankThresholds.'+name]=offset+0x6000
  symbols['RankThresholds.'+name+'.HighByte']=offset+0x6000;symbols['RankThresholds.'+name+'.LowByte']=offset+0x6001
 raw=source[0x4D2D:0x4D35]
 lines+=['                assert $ == #AD2D','                endmodule','','                module RankCaption',
  'Entry:'.ljust(16)+'db '+', '.join('#'+format(value,'02X') for value in raw),
  '                assert $ == #AD35','                endmodule']
 symbols['RankCaption.Entry']=0xAD2D
 return '\n'.join(lines)+'\n',symbols
