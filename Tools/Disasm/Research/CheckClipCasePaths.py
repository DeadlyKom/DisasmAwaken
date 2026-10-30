"""Проверка инициализации кэшированных произведений и числа выходных точек на всех ветвях."""
from pathlib import Path
import collections,json,re
ROOT=Path(__file__).resolve().parents[3]
PRODUCT={0xD8E2:'Top',0xD901:'Bottom',0xD920:'Left',0xD93F:'Right'}
APPEND={0xD95E:('Top',False),0xD961:('Top',True),0xD9A9:('Bottom',False),0xD9AC:('Bottom',True),
 0xD9F4:('Left',False),0xD9F7:('Left',True),0xDA52:('Right',False),0xDA55:('Right',True)}
DIFFERENCE={0xDADC:('Top','Left'),0xDAF0:('Top','Right'),0xDB04:('Bottom','Left'),0xDB18:('Bottom','Right')}


def paths(entry,ops):
 pending=[(entry,(),frozenset(),0)];visited=set();ends=set();checked=0
 while pending:
  state=pending.pop()
  if state in visited:continue
  visited.add(state);pc,stack,products,count=state;checked+=1
  assert len(stack)<8 and count<=2,(hex(entry),hex(pc),stack,products,count)
  def return_from(new_products=products,new_count=count):
   if stack:pending.append((stack[-1],stack[:-1],new_products,new_count))
   else:ends.add(('normal',new_count))
  if pc in PRODUCT:return_from(products|{PRODUCT[pc]});continue
  if pc in APPEND:
   product,cached=APPEND[pc]
   if cached:assert product in products,('uninitialized_cached_intersection',hex(entry),hex(pc),products)
   return_from(products|{product},count+1);continue
  if pc in DIFFERENCE:
   assert set(DIFFERENCE[pc])<=products,('uninitialized_difference',hex(entry),hex(pc),products)
   return_from();continue
  if pc in (0xDAB0,0xDABB,0xDAC6,0xDAD1,0xDB2C,0xDB37):return_from();continue
  if pc==0xDB42:return_from(products,count+1);continue
  if pc==0xDB59:
   assert not stack,('special_exit_with_nested_call',hex(entry),stack)
   ends.add(('special',count));continue
  if pc==0xD4DD:ends.add(('normal',count));continue
  item=ops[pc];operation=item['operation'];next_pc=pc+len(bytes.fromhex(item['hex']))
  if operation=='RET':return_from();continue
  match=re.fullmatch(r'(JP|CALL) (?:(M|P|NZ),)?#([0-9A-F]+)',operation)
  if match:
   kind,condition,literal=match.groups();target=int(literal,16)
   if condition:pending.append((next_pc,stack,products,count))
   pending.append((target,stack+(next_pc,) if kind=='CALL' else stack,products,count));continue
  assert not operation.startswith(('JP','JR','CALL','RET','DJNZ')),operation
  pending.append((next_pc,stack,products,count))
 return checked,ends


def main():
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 ops={i['address']:i for group in flow if group['name']=='Map' for i in group['instructions'] if i['slot']==7}
 dispatch=json.loads((ROOT/'Tools/Disasm/Reports/MapClipDispatch.json').read_text('utf-8'))
 rows=[]
 # Проверка обеих ветвей каждого условия даже при недостижимой геометрической комбинации, только при CornerBlock=1.
 for entry in dispatch['roots']:
  checked,ends=paths(entry,ops);rows.append(dict(entry=entry,abstract_states=checked,terminal_outcomes=sorted(ends)))
 report=dict(passed=True,method='all_conditional_paths_cached_product_definite_initialization_and_output_bound',roots_checked=len(rows),
  corner_block_precondition=1,conditional_branches_both_explored=True,maximum_output_points=2,
  initialized_products_proved=True,special_exits_have_no_nested_case_calls=True,roots=rows,
  arithmetic_ordering_independently_proved=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ClipCasePathsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='roots'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
