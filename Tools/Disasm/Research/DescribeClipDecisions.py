"""Физические пути обработчиков как явные условия и операции, не независимое геометрическое доказательство."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[3]
PRODUCT={0xD8E2:'Top',0xD901:'Bottom',0xD920:'Left',0xD93F:'Right'}
APPEND={0xD95E:'Top',0xD961:'Top',0xD9A9:'Bottom',0xD9AC:'Bottom',0xD9F4:'Left',0xD9F7:'Left',0xDA52:'Right',0xDA55:'Right'}
DIFFERENCE={0xDADC:('Top','Left'),0xDAF0:('Top','Right'),0xDB04:('Bottom','Left'),0xDB18:('Bottom','Right')}
CORNERS={0xDAB0:3,0xDABB:2,0xDAC6:1,0xDAD1:0}
ZONE={0:'I',1:'R',2:'L',4:'B',5:'BR',6:'BL',8:'T',9:'TR',10:'TL'}


def expand(entry,ops):
 pending=[(entry,(),(),(),None,0)];ends=[]
 while pending:
  pc,stack,conditions,actions,flag,marks=pending.pop()
  assert len(stack)<8 and len(actions)<20
  def returned(new_actions=actions,new_flag=None):
   if stack:pending.append((stack[-1],stack[:-1],conditions,new_actions,new_flag,marks))
   else:ends.append(dict(conditions=conditions,actions=new_actions,exit='normal'))
  if pc in PRODUCT:returned();continue
  if pc in DIFFERENCE:returned(new_flag=('product',*DIFFERENCE[pc]));continue
  if pc in APPEND:returned(actions+(('intersection',APPEND[pc]),));continue
  if pc in CORNERS:returned(actions+(('corner',CORNERS[pc]),));continue
  if pc in (0xDB2C,0xDB37):returned(new_flag=('delta','X' if pc==0xDB2C else 'Y'));continue
  if pc==0xDB42:returned(actions+(('second',),));continue
  if pc==0xDB59:assert not stack;ends.append(dict(conditions=conditions,actions=actions,exit='special'));continue
  item=ops[pc];operation=item['operation'];next_pc=pc+len(bytes.fromhex(item['hex']))
  if operation=='RET':returned(new_flag=flag);continue
  match=re.fullmatch(r'(JP|CALL) (?:(M|P|NZ),)?#([0-9A-F]+)',operation)
  if match:
   kind,condition,literal=match.groups();target=int(literal,16)
   if condition:
    assert flag is not None,(hex(entry),hex(pc),'unexplained_condition')
    pending.append((next_pc,stack,conditions+((flag,condition,False),),actions,flag,marks))
    conditions=conditions+((flag,condition,True),)
   pending.append((target,stack+(next_pc,) if kind=='CALL' else stack,conditions,actions,flag,marks));continue
  match=re.fullmatch(r'(BIT|SET) ([0-3]),\(HL\)',operation)
  if match:
   kind,bit=match.groups();bit=int(bit)
   if kind=='BIT':flag=('seen',bit,marks)
   else:actions=actions+(('mark',bit),);marks|=1<<bit
  else:assert operation=='LD HL,#DE39',(hex(pc),operation)
  pending.append((next_pc,stack,conditions,actions,flag,marks))
 return ends


def describe_condition(condition):
 flag,code,taken=condition
 if flag[0]=='seen':return ('уже отмечен ' if taken else 'ещё не отмечен ')+('BR','BL','TR','TL')[flag[1]]+' с учётом предыдущих отметок этого пути'
 formula=(flag[1]+'Product−'+flag[2]+'Product') if flag[0]=='product' else flag[1]+'2−'+flag[1]+'1'
 negative=(code=='M')==taken
 return formula+(' < 0' if negative else ' ≥ 0')+' по знаковому биту обёрнутой разности'


def describe_action(action):
 kind,*args=action
 if kind=='second':return 'добавить вторую точку'
 if kind=='intersection':return 'добавить пересечение '+args[0]
 if kind=='mark':return 'отметить '+('BR','BL','TR','TL')[args[0]]
 return 'запросить угол '+('BR','BL','TR','TL')[args[0]]


def main():
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 ops={i['address']:i for g in flow if g['name']=='Map' for i in g['instructions'] if i['slot']==7}
 dispatch=json.loads((ROOT/'Tools/Disasm/Reports/MapClipDispatch.json').read_text('utf-8'))
 # Чтение всех физических табличных целей до возможной перезаписи нулевой строки рабочими данными.
 rows=dispatch.get('entries',dispatch.get('pairs'))
 assert rows is not None,dispatch.keys()
 cases=[]
 for row in rows:
  first=row.get('first_code',row.get('first'));second=row.get('second_code',row.get('second'));entry=row.get('target')
  assert first in ZONE and second in ZONE and entry is not None,row
  cases.append(dict(first=first,second=second,entry=entry,paths=expand(entry,ops)))
 report=dict(method='symbolic_original_control_flow_to_explicit_semantic_decision_paths',cases=cases,
  all_conditions_have_explained_provenance=True,independent_geometry_proof=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipDecisionPaths.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 lines=['# Условия всех физических табличных входов отсечения','',
  '[Исходные обработчики](../Source/Map/MapClipCases.asm) и [общий договор](ClipCases.md).',
  '', 'I означает внутреннюю точку, R/L/B/T — правую, левую, нижнюю и верхнюю внешнюю сторону. Составные имена обозначают угловую зону.',
  '', 'Это раскрытие исходного графа, а не независимое доказательство геометрии. Произведения заданы формулами в [ClipProducts](ClipProducts.md). Разность произведений оборачивается до 32 бит, разность координат до 16 бит. Равенство входит в неотрицательную ветвь.',
  '', 'Пересечение использует исходное однокомплементное деление и байтовые ограничения из [ClipIntersections](ClipIntersections.md). Запрос угла добавляет точку только при BlockCode=0. Отметка изменяет SeenFlags независимо от BlockCode. Проверка отметки относится к состоянию до следующего SET, этот SET не меняет флаги.',
  '', 'Обычный выход использует общий D4DD, специальный — UnwindClipFrame. Договоры кадров описаны в [ClipTail](ClipTail.md). Входы с внутренней первой точкой перечислены физически, D48B перед выбором меняет такую точку местами со второй.', '']
 for case in cases:
  lines+=['## '+ZONE[case['first']]+' → '+ZONE[case['second']]+' ('+format(case['entry'],'04X')+')','']
  for path in case['paths']:
   condition=' и '.join(describe_condition(c) for c in path['conditions']) or 'без дополнительных условий'
   actions=', затем '.join(describe_action(a) for a in path['actions']) or 'выходные точки и отметки не добавляются'
   lines+=['- '+condition+' — '+actions+', '+('специальный выход' if path['exit']=='special' else 'обычный выход')+'.']
  lines+=['']
 (ROOT/'Docs/ClipCaseDecisions.md').write_text('\n'.join(lines),'utf-8')
 print(json.dumps(dict(cases=len(cases),paths=sum(len(c['paths']) for c in cases),independent_geometry_proof=False)))


if __name__=='__main__':main()
