"""Физические три слова конца HR-результата перед общим потоком байтов и битов."""


def final_lines(block,stem):
 def line(code,note='',label=''):
  text=(label+':').ljust(16)+code if label else ' '*16+code
  return text.ljust(80)+'; '+note if note else text
 result=[line('FPackedFinalBytes {','исходные последние шесть байтов результата','FinalBytes')]
 for index,field in enumerate(('BytesMinus6','BytesMinus4','BytesMinus2')):
  value=int.from_bytes(block[6+2*index:8+2*index],'little');code='#'+format(value,'04X')+(',' if index<2 else '')
  result.append(line(code,field+', пара финальных байтов результата'))
 result.extend((line('}'),line('incbin "'+stem+'.Bitstream.bin"','общий поток битовых слов и литералов после префикса','Bitstream')))
 return result
