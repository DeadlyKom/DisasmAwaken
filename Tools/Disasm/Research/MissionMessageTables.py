"""Два исходных CR/LF-предупреждения тела нажатия миссии."""
RANGES=((0x11EE,0x11F9,'Source/Station/Data/MissionTonnageMessage.asm','MissionTonnageMessage'),
 (0x1261,0x1271,'Source/Station/Data/MissionCancelMessage.asm','MissionCancelMessage'))


def render(source):
 outputs={};symbols={}
 for begin,end,path,module in RANGES:
  raw=source[begin:end]
  if raw[0]!=13 or raw[-1]!=10:raise ValueError('Не подтверждены CR и LF предупреждения миссии')
  lines=['                module '+module,'; Документация [действия миссии](../../../Docs/MissionAction.md)',
   '                assert $ == #'+format(begin+0x5D54,'04X'),
   'Entry:'.ljust(16)+'db '+', '.join('#'+format(value,'02X') for value in raw),
   '                assert $ == #'+format(end+0x5D54,'04X'),'                endmodule']
  outputs[path]='\n'.join(lines)+'\n';symbols[module+'.Entry']=begin+0x5D54
 return outputs,symbols
