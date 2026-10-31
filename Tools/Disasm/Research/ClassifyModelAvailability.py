"""Физические записи доступности моделей, точечный кандидат без сборки."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from ModelAvailabilityTable import PATH,START,END,render,name_operands
from VerifySources import main as verify
CANDIDATE=ROOT/'Tools/Disasm/Research/Candidates/ModelAvailabilityScoped'
HISTORY=ROOT/'Tools/Disasm/Research/History/BeforeModelAvailability'


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 assert not CANDIDATE.exists() and not HISTORY.exists()
 raw=payload(4);text,labels=render(raw);pending={ROOT/PATH:text};read=lambda name:json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'));source_map=read('SourceMap');old=next(e for e in source_map if e['slot']==4 and e['offset']<=START<e['offset']+e['length']);original=ROOT/old['path'];assert old['kind']=='unclassified' and old['offset']+old['length']==END and original.read_bytes()==raw[old['offset']:END]
 prefix='Source/Resources/04_STATIONF/BeforeModelAvailability.bin';binary=raw[old['offset']:START];index=source_map.index(old);source_map[index:index+1]=[dict(old,length=START-old['offset'],path=prefix,sha256=hashlib.sha256(binary).hexdigest()),dict(old,offset=START,length=END-START,kind='typed_data',path=PATH,origin=0x94BC,sha256=hashlib.sha256(raw[START:END]).hexdigest())]
 symbols=read('Symbols');assert not symbols.keys()&labels.keys();symbols.update(labels);inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(e['length'] for e in source_map if e['kind']==kind) for kind in sorted({e['kind'] for e in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(e['kind'] for e in source_map))
 for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'Includes/Structs/Include.inc';s=p.read_text('utf-8');assert 'struct FModelAvailability' not in s;block='                ; начальные индексы ценового рынка для одного числового уровня системы\n                struct FModelAvailability\n'+('ShipBase        db #00').ljust(80)+'; начальный индекс кораблей 0..5, ноль открывает все шесть рыночных строк\n'+('SkimmerBase     db #00').ljust(80)+'; начальный индекс скимеров 0..3, ноль открывает все четыре строки\n                ends\n                assert FModelAvailability == #02\n\n';pending[p]=s.replace('                endif\n',block+'                endif\n')
 p=ROOT/'Source/Files/04_STATIONF.inc';s=p.read_text('utf-8');needle='                incbin "../Resources/04_STATIONF/'+original.name+'"';assert s.count(needle)==1;pending[p]=s.replace(needle,'                incbin "../Resources/04_STATIONF/BeforeModelAvailability.bin"\n                assert $ == #34BC\n                disp #94BC\n                include "../Station/Data/ModelAvailability.asm"\n                ent\n                assert $ == #34DC')
 p=ROOT/'Source/Station/DrawItem25.asm';s=p.read_text('utf-8');s=name_operands('Station',0x67E0,s);s=s.replace('                DEC L\n','                ; расчёт смещения двухбайтовой FModelAvailability по уровню 1..16\n                DEC L\n').replace('                INC HL\n','                ; выбор поля SkimmerBase соседней компоненты той же физической записи\n                INC HL\n');pending[p]=s
 plan=[]
 # Отдельный кандидат хранит только затронутые файлы и префикс, полного снимка проекта нет.
 for p,value in {**pending,ROOT/prefix:binary}.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=CANDIDATE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 for rel,before,data in plan:assert (ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists();assert (CANDIDATE/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=HISTORY/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 target=HISTORY/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только заменённой бинарной копии, оригинал образа и извлечение не меняются.
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/04_STATIONF') and original.read_bytes()==(HISTORY/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,records=16,record_size=2,typed_bytes=32,source_labels=48,original_values_preserved=True,level_domain_from_describe_current_key='1..16',next_physical_table='MarketCategories at 94DC',scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ModelAvailabilityClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
