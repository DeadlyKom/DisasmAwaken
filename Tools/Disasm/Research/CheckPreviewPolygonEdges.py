"""Оба обновления ребра, все 511 наклонов при каждой допустимой экранной высоте.

Документация: ../../../Docs/PreviewPolygonFill.md#полный-m1-обновления-ребра
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewEdgeRasterOracle import arithmetic


def refresh_costs(raw):
 # Проверка всех кодов двух цепочек, кольцевых переходников и настоящего делителя.
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 instructions={i['address']:bytes.fromhex(i['hex']) for region in flow if region['name']=='D3D'
               for i in region['instructions'] if 0xD282<=i['address']<0xD40F or 0xD4DF<=i['address']<0xD518}
 for address,code in instructions.items():assert raw[address-0xC000:address-0xC000+len(code)]==code
 def cost(first,end):
  total=0;pc=first
  while pc<end:
   code=instructions[pc];total+=2 if code[0] in (0xCB,0xDD,0xED,0xFD) else 1;pc+=len(code)
  assert pc==end
  return total
 # Расчёт независимых прямых диапазонов для фикстуры из двух точек и одного кандидата.
 left=(cost(0xD28C,0xD299)+cost(0xD285,0xD28C)+cost(0xD29A,0xD2B6),
       cost(0xD2B6,0xD2BA),cost(0xD2BA,0xD2C4),cost(0xD2C4,0xD2E4),
       cost(0xD2E4,0xD301),cost(0xD301,0xD312),cost(0xD312,0xD317),
       cost(0xD317,0xD33C),cost(0xD33C,0xD34B))
 right=(cost(0xD350,0xD380),cost(0xD380,0xD384),cost(0xD384,0xD38E),
        cost(0xD38E,0xD3AD),cost(0xD3AD,0xD3C9),cost(0xD3C9,0xD3D9),
        cost(0xD3D9,0xD3DE),cost(0xD3DE,0xD401),cost(0xD401,0xD40F))
 return instructions,(left,right)


def expected_edge_m1(costs,delta,height):
 head,positive,divide_start,fraction,exact,short_positive,negative,long_negative,short_negative=costs
 magnitude=abs(delta)
 # Расчёт стоимости делителя по математическому частному, включая его RET.
 division=41+((magnitude//height)^255).bit_count()
 if delta<0:return head+negative+(short_negative if magnitude<height else long_negative+division)
 if magnitude<height:return head+positive+short_positive
 return head+positive+divide_start+division+(fraction if magnitude%height else exact)


def check_skipped_candidates(raw,instructions,costs):
 m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0xFFE0,'HL':0xC03A,'DE':0xD169,'BC':0x50B3,'IX':0x2468,
  'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0;seeds=set();visited=set();search_bounds=[999,0]
 for rejected in range(7):
  count=rejected+2
  for pattern in range(3):
   for height in (1,7,31,118):
    for delta in (-255,-7,-1,0,1,7,255):
     for right in (False,True):
      for start_index in (0,count-1):
       # Создание конечного кольца, промежуточные колонки отличаются от начальной.
       y=73;x=max(0,-delta);direction=1 if right else -1
       vertices=[[0,y] for _ in range(count)];vertices[start_index]=[x,y]
       cursor=start_index;search=0
       for index in range(1,rejected+2):
        if not right:search+=5 if cursor==0 else 3
        else:search+=5
        cursor=(cursor+direction)%count
        if index==rejected+1:
         vertices[cursor]=[x+delta,y+height];search+=4
        else:
         row=y if pattern==0 or pattern==2 and index&1 else 0
         vertices[cursor]=[(index*73+cases*29)&255,row];search+=3 if row==y else 4
       m.recording=False;m[0xC800:0xC800+2*count]=[v for point in vertices for v in point]
       m[0xD35F]=2*count-1;pointer=0xD358 if right else 0xD290
       m[pointer:pointer+2]=[2*start_index+1,0xC8]
       s.registers[:]=initial;r=s.registers;r[0:2]=[y,cases&255]
       r[14]=cases&255;r[15]=(cases*73)&255;r[26]=cases&1;r[27]=cases%3
       before=list(r);seeds.add(r[15]);r[24]=0xD350 if right else 0xD28C
       stop=0xD24A if right else 0xD242;m.writes=[];m.recording=True;measured=0
       for _ in range(512):
        if r[24]==stop:break
        pc=r[24];visited.add(pc);code=instructions[pc]
        for offset,value in enumerate(code):
         if pc+offset not in (0xD290,0xD291,0xD358,0xD359,0xD35F):assert m[pc+offset]==value
        step=2 if code[0] in (0xCB,0xDD,0xED,0xFD) else 1;old_r=r[15]
        s.run();measured+=step
        assert r[15]==(old_r&128)|((old_r+step)&127)
       else:raise AssertionError(('поиск восходящего ребра не завершён',rejected,pattern,right))
       m.recording=False
       # Расчёт полного M1 из независимого обхода кольца и арифметической ветви.
       expected=expected_edge_m1(costs[int(right)],delta,height)+search-9
       assert measured==expected,(rejected,pattern,height,delta,right,start_index,measured,expected)
       assert r[15]==(before[15]&128)|((before[15]+expected)&127)
       assert r[8:15]==before[8:15] and r[26:28]==before[26:28]
       assert m[pointer:pointer+2]==[2*cursor+1,0xC8]
       haddr,saddr,endaddr=(0xD233,0xD22F,0xD243) if right else (0xD227,0xD223,0xD23F)
       q,remainder=divmod(abs(delta),height);wide=abs(delta)>=height
       subtract=(0 if remainder==0 and wide else height-remainder) if delta>=0 else remainder
       assert (m[haddr],m[saddr],m[endaddr])==(height,subtract,y+height)
       expected_e=((q^255)>>(1 if right and delta<0 else 0)) if wide else x
       assert r[4:8]==[0xD1,expected_e,0xC0,0xD1]
       assert r[2:4]==before[2:4] and r[16:18]==before[16:18]
       if not right:assert r[:2]==before[:2]
       allowed={haddr,saddr,endaddr,pointer,pointer+1,*range(0xFFDC if right else 0xFFDA,0xFFE0)}
       if right:allowed.add(0xD239);assert m[0xD239]==y+1
       assert all(address in allowed for address,value in m.writes)
       search_bounds[0]=min(search_bounds[0],search);search_bounds[1]=max(search_bounds[1],search)
       cases+=1
 assert seeds==set(range(256))
 assert {0xD285,0xD299,0xD29C,0xD29E,0xD34B,0xD366,0xD368}<=visited
 return dict(cases=cases,rejected_candidates_range=[0,6],points_range=[2,8],
  equal_and_lower_rows=True,both_wrap_directions=True,start_at_first_and_last_point=True,
  search_m1_bounds=search_bounds,initial_R_values=256,full_m1_and_each_R_step_checked=True,
  selected_endpoint_initial_column_and_output_operands_checked=True,
  all_joint_inputs_exhausted=False,native_execution=False,irq_executed=False)


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 instructions,costs=refresh_costs(raw);refresh_seeds=set();m1_bounds={};full_m1_total=0
 initial=get_registers({'SP':0xFFE0,'HL':0xC03A,'DE':0xD169,'BC':0x50B3,'AF':0x005D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0;branches={}
 for height in range(1,192):
  for delta in range(-255,256):
   start=max(0,-delta);end=start+delta;m.recording=False;m[0xC800:0xC804]=[start,0,end,height];m[0xD35F]=3
   for right in (False,True):
    pointer=0xD358 if right else 0xD290;m.recording=False;m[pointer:pointer+2]=[1,0xC8]
    s.registers[:]=initial;r=s.registers;r[14]=cases&255;r[15]=(cases*73)&255;r[26]=cases&1;r[27]=cases%3
    saved_system=(r[14],r[26],r[27]);initial_r=r[15];refresh_seeds.add(initial_r)
    r[24]=0xD350 if right else 0xD28C;stop=0xD24A if right else 0xD242
    m.recording=True;m.writes=[];measured_m1=0
    for _ in range(256):
     if r[24]==stop:break
     pc=r[24];code=instructions[pc]
     # Проверка команд, только три известных операнда меняются подготовкой фикстуры.
     for offset,value in enumerate(code):
      if pc+offset not in (0xD290,0xD291,0xD358,0xD359,0xD35F):assert m[pc+offset]==value
     count=2 if code[0] in (0xCB,0xDD,0xED,0xFD) else 1;before_r=r[15]
     s.run();measured_m1+=count
     assert r[15]==(before_r&128)|((before_r+count)&127)
    else:raise AssertionError(('edge instruction limit',height,delta,right))
    predicted_m1=expected_edge_m1(costs[int(right)],delta,height)
    assert measured_m1==predicted_m1,(height,delta,right,measured_m1,predicted_m1)
    assert r[15]==(initial_r&128)|((initial_r+predicted_m1)&127)
    assert (r[14],r[26],r[27])==saved_system
    full_m1_total+=measured_m1
    magnitude=abs(delta);quotient,remainder=divmod(magnitude,height);wide=magnitude>=height
    # Расчёт целого упакованного шага и вычитаемой дробной части независимо от сдвигов кода.
    step=-((-delta)//height) if delta else 1;packed=(0x2000+32*step)&65535
    subtract=(0 if remainder==0 and wide else height-remainder) if delta>=0 else remainder
    encoded=(quotient^255)>>(1 if right and delta<0 else 0)
    expected_e=encoded if wide else start
    if not right:af=tuple(initial[:2])
    elif wide:
     high=packed>>8;af=(high,arithmetic((high-0x20)&255,0x20)[1])
    elif delta>=0:af=arithmetic(0,(delta-height)&255,True)
    else:
     _,flags=arithmetic(magnitude,height,True);af=(magnitude,(flags&~0x28)|(height&0x28))
    assert tuple(r[:8])==(*af,initial[2],initial[3],0xD1,expected_e,0xC0,0xD1),(height,delta,right,r[:8],af,packed)
    assert r[8:13]==initial[8:13] and r[16:18]==initial[16:18]
    assert r[22:24]==([height//2,initial[23]] if right else [initial[22],height//2])
    pair=(r[20]*256+r[21]) if right else (r[18]*256+r[19]);assert pair==packed
    assert r[18:20]==initial[18:20] if right else r[20:22]==initial[20:22]
    haddr=0xD233 if right else 0xD227;saddr=0xD22F if right else 0xD223;endaddr=0xD243 if right else 0xD23F
    assert (m[haddr],m[saddr],m[endaddr],m[pointer],m[pointer+1])==(height,subtract,height,3,0xC8)
    allowed={haddr,saddr,endaddr,pointer,pointer+1,*range(0xFFDC if right else 0xFFDA,0xFFE0)}
    if right:allowed.add(0xD239);assert m[0xD239]==1
    assert all(p in allowed for p,v in m.writes)
    key=('right' if right else 'left')+('_negative' if delta<0 else '_positive')+('_wide' if wide else '_short')
    branches[key]=branches.get(key,0)+1;cases+=1
    bounds=m1_bounds.setdefault(key,[predicted_m1,predicted_m1]);bounds[0]=min(bounds[0],predicted_m1);bounds[1]=max(bounds[1],predicted_m1)
 wrappers=0;wrapper_refresh_seeds=set()
 assert bytes(m[0xD282:0xD28C])==bytes.fromhex('c350d33a5fd36fc39ad2')
 assert bytes(m[0xD34B:0xD350])==bytes.fromhex('2e01c364d3')
 # Проверка обеих обёрток кольца и прямого JP к правой цепочке на всех входных F.
 for flags in range(256):
  for entry,stop in ((0xD282,0xD350),(0xD285,0xD29A),(0xD34B,0xD364)):
   for index in (range(1,256,2) if entry==0xD285 else range(256) if entry==0xD34B else (1,)):
    m.recording=False;m[0xD35F]=index;s.registers[:]=initial;r=s.registers;r[1]=flags;r[6]=0xC8;r[7]=index
    r[14]=index;r[15]=flags^index;r[26]=flags&1;r[27]=flags%3;saved=r[:];wrapper_refresh_seeds.add(r[15])
    if entry==0xD285:saved[0]=index;saved[7]=index
    elif entry==0xD34B:saved[7]=1
    m.recording=True;m.writes=[];s.run(start=entry,stop=stop)
    assert r[:13]==saved[:13] and r[16:24]==saved[16:24] and not m.writes;wrappers+=1
    m1={0xD282:1,0xD285:3,0xD34B:2}[entry]
    assert r[15]==(saved[15]&128)|((saved[15]+m1)&127)
    assert r[14]==saved[14] and r[26:28]==saved[26:28]
 report=dict(passed=True,cases=cases,wrapper_cases=wrappers,branches=branches,all_191_heights_and_511_signed_slopes=True,exact_full_main_alternate_and_index_context=True,left_af_preserved=True,right_short_and_wide_af_checked=True,negative_right_half_quotient_preserved=True,exact_operand_targets_and_values=True,wrapped_left_chain_checked=True,both_wrap_helpers_and_right_selector_all_flags_checked=True,temporary_stack_writes_bounded=True,cpu_return_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 assert wrapper_refresh_seeds==set(range(256))
 report.update(wrapper_m1_by_entry={'D282':1,'D285':3,'D34B':2},wrapper_R_initial_values=256,
  wrapper_R_bit7_and_I_IM_IFF_preserved=True,wrapper_original_opcode_bytes_checked=True,
  whole_edge_update_R_cost_proved=True,edge_R_scope='all_two_point_screen_slopes_and_selected_skipping_rings',
  edge_m1_by_path_bounds=m1_bounds,edge_full_m1_total=full_m1_total,
  edge_R_initial_values=len(refresh_seeds),edge_each_R_step_and_full_m1_checked=True,
  additional_skipped_ring_candidates=check_skipped_candidates(raw,instructions,costs),
  additional_skipped_ring_candidates_R_cost_proved=True,wrapper_R_full_input_product=False)
 assert refresh_seeds==set(range(256))
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonEdgesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
