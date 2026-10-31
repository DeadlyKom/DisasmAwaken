"""Исходный, не подменённый сценарий LANG для событий 9, 10 и 11."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWeightedLoad import reference as weighted_load


def store7(old,result):
    result&=65535
    low=127 if result>>8 else result&127
    return (old&128)|low


def reference(event,stock,cargo,price,credits,projected_load,capacity):
    messages=[];stop=False
    if event==9:
        # Исходный Q не входит в таблицу чтения, строка проверки наличия пропускается.
        if price>credits:messages=[0];stop=True
        elif projected_load>capacity:messages=[2];stop=True
        elif cargo>=120:messages=[5];stop=True
        else:
            cargo=store7(cargo,cargo+1);credits=max(0,credits-price);stock=store7(stock,max(0,(stock&127)-1))
    else:
        if cargo==0:messages=[8];stop=True
        elif stock&128:
            messages=[9];stop=True;credits=max(0,credits-1000);cargo=store7(cargo,0)
        else:
            amount=1 if event==10 else cargo
            total=min(65535,credits+price*amount)
            if total>65000:messages=[10]
            credits=total;stock=store7(stock,(stock&127)+amount);cargo=store7(cargo,cargo-amount)
    return stock,cargo,credits,messages,stop


def main():
    _,_,banks=make_context();manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=list(lang)
    functions=json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_text('utf-8'));skip_line=next(f['address'] for f in functions if f['region']=='Text' and f['name']=='SkipLine')
    raw_script=lang[0xA8F:];active=raw_script[:raw_script.index(0)+1];q_address=0xCA8F+active.index(b'Qn');assert 81 not in [banks[6][0x983+3*i] for i in range(36)]
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=invalid_q=overflow_continued=empty_stock_buys=illegal_fines=0;counts={9:0,10:0,11:0};messages_seen={};ports=0
    def execute(event,stock,cargo,price,credits,capacity=255):
        nonlocal cases,invalid_q,overflow_continued,empty_stock_buys,illegal_fines,ports
        page=0x16 if cases&1 else 0x1E;m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
        index=cases%30;base=index//2;selected=index-base;m[0x6306]=page;m[0x983A]=event;m[0x7026]=base;m[0x7068]=selected;m[0x984A]=255;m[0x9851]=capacity
        # Остальные грузы и оснащение пусты, исходные таблицы физических весов не меняются.
        put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14));put(m,0x984E,credits.to_bytes(2,'little'))
        m[0x9555+2*index]=stock;m[0x9556+2*index]=price;m[0x9852+2*index]=cargo
        put(m,0x6E8B,[10,0]);put(m,0x9CA6,[0xDE,0xF3]);put(m,0xF3DE,[0x8A,0x6E,1,1]);m[0x9A82]=0xA7;m[0x6E91]=0xA7
        projected_load=weighted_load(bytearray(m[0:65536]),index)[0]
        put(m,0x7FFE,[255,63]);s.registers[:]=initial;s.registers[PC]=0xC000;observed=[];q_skips=0
        for _ in range(220000):
            r=s.registers;pc=r[PC]
            if pc==0x3FFF:break
            if pc==0xA85F:observed.append(r[A])
            if pc==skip_line and r[8]*256+r[9]==q_address+1:q_skips+=1
            s.run()
        else:raise AssertionError(('instruction_limit',event,stock,cargo,price,credits,index,hex(s.registers[PC])))
        expected_stock,expected_cargo,expected_credits,expected_messages,stop=reference(event,stock,cargo,price,credits,projected_load,capacity)
        actual=(m[0x9555+2*index],m[0x9852+2*index],m[0x984E]+256*m[0x984F])
        assert actual==(expected_stock,expected_cargo,expected_credits),(event,stock,cargo,price,credits,index,actual,(expected_stock,expected_cargo,expected_credits),observed)
        assert observed==expected_messages and m[0x6E91]==(expected_messages[-1] if expected_messages else 0xA7)
        assert m.banks[6][0x28]==int(stop) and s.registers[SP]==0x8000 and m.o7ffd==page and m[0x6306]==page
        assert bytes(m.banks[6][0xA8F:len(lang)])==raw_script
        assert q_skips==int(event==9),(event,stock,cargo,price,credits,q_skips,hex(q_address))
        memory=bytearray(m[0:65536]);assert m[0x9850]==weighted_load(memory,0xC0DB)[0]
        if expected_messages:assert m[0x9A82]==0
        invalid_q+=q_skips;overflow_continued+=expected_messages==[10];illegal_fines+=expected_messages==[9]
        empty_stock_buys+=event==9 and (stock&127)==0 and not expected_messages
        for message in expected_messages:messages_seen[message]=messages_seen.get(message,0)+1
        counts[event]+=1;cases+=1;ports+=len(trace.writes)
    # Проверка каждого байта количества и маркера в оригинальных трёх ветвях.
    for value in range(256):
        execute(9,value,value&127,17,2000)
        execute(10,value^128,value,17,65000)
        execute(11,value^128,value,17,65000)
    # Проверка денежных границ, нулевого остатка, лимита 120 и обоих старших разрядов.
    for event in (9,10,11):
        for price in (0,1,17,255):
            for credits in (0,1,999,1000,64999,65000,65535):
                for cargo in (0,1,119,120,127,128,255):
                    for stock in (0,1,127,128,129,255):execute(event,stock,cargo,price,credits)
    # Проверка всех вместимостей и границ шестнадцатой доли по всем тридцати индексам исходных весов.
    for capacity in range(256):execute(9,4,3,1,1000,capacity)
    for _ in range(30):
        for cargo in (0,15,16,119):
            for capacity in (0,1,127):execute(9,4,cargo,1,1000,capacity)
    report=dict(passed=True,cases=cases,per_event=counts,all_quantity_and_marker_bytes=True,original_script_bytes_unchanged=True,
                script_start=0xCA8F,active_script_bytes=len(active),invalid_q_address=q_address,invalid_q_skip_cases=invalid_q,
                overflow_message_then_trade_cases=overflow_continued,empty_stock_purchase_cases=empty_stock_buys,illegal_market_fine_cases=illegal_fines,
                queued_messages=messages_seen,ports_checked_as_real_banking=ports,all_ship_capacity_bytes=True,
                actual_interpreter_and_original_script_executed=True,actual_weight_tables_preserved=True,
                station_display_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/OriginalTradeScriptVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
