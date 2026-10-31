"""Точечная типизация 22 исходных байтов параметров и масок рёбер, без сборки."""
from pathlib import Path
import collections,contextlib,hashlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm')]
from Analyze import payload
from PreviewEdgeData import TABLES,MASK_PATH,render,render_masks
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 candidate=ROOT/'Tools/Disasm/Research/Candidates/PreviewEdgeDataScoped';history=ROOT/'Tools/Disasm/Research/History/BeforePreviewEdgeData'
 assert not candidate.exists() and not history.exists()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 assert read('PreviewEdgeRasterVerification')['passed'];raw=payload(6);pending={};symbols=read('Symbols')
 for table in TABLES:
  text,labels=render(raw,table);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/table[1]]=text
 text,labels=render_masks(raw);assert not symbols.keys()&labels.keys();symbols.update(labels);pending[ROOT/MASK_PATH]=text
 p=ROOT/'Includes/Structs/Include.inc';text=p.read_text('utf-8');block='                ; Документация [физические параметры рёбер](../../Docs/PreviewEdgeRaster.md)\n'
 for module,path,start,end,structure,fields,names in TABLES:
  assert 'struct '+structure not in text;block+='                struct '+structure+'\n'
  for field,width,meaning in fields:block+=(field.ljust(16)+('dw #0000' if width==2 else 'db #00')).ljust(80)+'; '+meaning+'\n'
  block+='                ends\n                assert '+structure+' == #'+format(end-start,'02X')+'\n\n'
 pending[p]=text.replace('                endif\n',block+'                endif\n')
 def typed(table):return table[2],table[3],'typed_data',table[1]
 replacements=(
  ('Source/Resources/06_D3D/AfterSceneMatrix.bin',(
   (0x21E,0x24B,'unclassified','Source/Resources/06_D3D/BeforeEdgeEndpoints.bin'),typed(TABLES[0]),
   (0x24F,0x26F,'unclassified','Source/Resources/06_D3D/BetweenEdgeEndpointsMode.bin'),typed(TABLES[1]),
   (0x271,0x300,'unclassified','Source/Resources/06_D3D/AfterEdgeMode.bin'))),
  ('Source/Resources/06_D3D/AfterQueueStorage.bin',(
   (0x7FC,0xDB0,'unclassified','Source/Resources/06_D3D/BeforePixelMasks.bin'),
   (0xDB0,0xDC0,'typed_data',MASK_PATH),
   (0xDC0,0xE40,'unclassified','Source/Resources/06_D3D/AfterPixelMasks.bin'))))
 source_map=read('SourceMap');p=ROOT/'Source/Files/06_D3D.inc';include=p.read_text('utf-8');originals=[]
 # Проверка полного покрытия только двух явно выбранных исходных областей.
 for old_path,parts in replacements:
  old=next(v for v in source_map if v['path']==old_path);original=ROOT/old_path;originals.append(original);assert original.read_bytes()==raw[old['offset']:old['offset']+old['length']]
  mapped=[];rows=[];position=old['offset']
  for start,end,kind,target in parts:
   assert start==position and start<end;position=end;blob=raw[start:end];mapped.append(dict(old,offset=start,length=end-start,kind=kind,path=target,origin=0xC000+start if kind=='typed_data' else None,sha256=hashlib.sha256(blob).hexdigest()))
   if kind=='typed_data':rows+=['                disp #'+format(0xC000+start,'04X'),'                include "../D3D/Data/'+Path(target).name+'"','                ent']
   else:pending[ROOT/target]=blob;rows.append('                incbin "../Resources/06_D3D/'+Path(target).name+'"')
   rows.append('                assert $ == #'+format(end,'04X'))
  assert position==old['offset']+old['length'];idx=source_map.index(old);source_map[idx:idx+1]=mapped
  needle='                incbin "../Resources/06_D3D/'+original.name+'"';assert include.count(needle)==1;include=include.replace(needle,'\n'.join(rows))
 pending[p]=include
 p=ROOT/'Tools/Disasm/VerifySources.py';text=p.read_text('utf-8');needle='    preview_scene_records = {}';assert text.count(needle)==1
 text=text.replace(needle,'    from PreviewEdgeData import TABLES as PREVIEW_EDGE_TABLES\n'+needle).replace('(*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE):','(*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE, *PREVIEW_EDGE_TABLES):')
 needle='    # Проверка исходных DB свёрнутых квадратов';assert text.count(needle)==1
 check="""    # Проверка двух исходных таблиц пиксельных масок и их фактического размещения.
    from PreviewEdgeData import MASK_PATH, parse_bytes as parse_mask_bytes
    preview_pixel_masks = 0
    mask_entries = [item for item in source_map if item['path'] == MASK_PATH]
    if mask_entries:
        if len(mask_entries) != 1:
            raise ValueError('Неоднозначная регистрация масок рёбер')
        item = mask_entries[0]
        if (item['slot'],item['offset'],item['length'],item['origin']) != (6,0xDB0,16,0xCDB0):
            raise ValueError('Изменилось размещение масок рёбер')
        raw, labels = parse_mask_bytes((ROOT/MASK_PATH).read_text('utf-8'),0xCDB0)
        if raw != sources[6][0xDB0:0xDC0] or raw != bytes([128>>i for i in range(8)]+[255^(128>>i) for i in range(8)]):
            raise ValueError('Изменились исходные маски пикселя')
        if any(symbols.get(key.upper()) != value for key,value in labels.items()):
            raise ValueError('Изменились метки масок пикселя')
        preview_pixel_masks = 16

"""
 text=text.replace(needle,check+needle);needle="    report['preview_projected_vertices'] = preview_projected_vertices";assert needle in text;pending[p]=text.replace(needle,needle+"\n    report['preview_pixel_masks'] = preview_pixel_masks")
 p=ROOT/'Tools/Disasm/Research/ExportSources.py';text=p.read_text('utf-8');needle='    for table in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE):';assert text.count(needle)==1
 text=text.replace(needle,'    from PreviewEdgeData import TABLES as PREVIEW_EDGE_TABLES, MASK_PATH as EDGE_MASK_PATH, render_masks as render_edge_masks\n    for table in (*PREVIEW_SCENE_TABLES, PREVIEW_DRAW_STATE_TABLE, *PREVIEW_EDGE_TABLES):')
 needle='    # Исходная страница свёрнутых квадратов';assert text.count(needle)==1
 pending[p]=text.replace(needle,"    text, labels = render_edge_masks(data_by_slot[6])\n    write(EDGE_MASK_PATH,text)\n    symbols.update(labels)\n    special[6,0xDB0] = (0xDC0,EDGE_MASK_PATH,0xCDB0)\n"+needle)
 p=ROOT/'Docs/PreviewEdgeRaster.md';pending[p]=p.read_text('utf-8')+'\nФизические параметры оформлены как [PreviewEdgeEndpoints](../Source/D3D/Data/PreviewEdgeEndpoints.asm), [PreviewEdgeMode](../Source/D3D/Data/PreviewEdgeMode.asm) и [PreviewPixelMasks](../Source/D3D/Data/PreviewPixelMasks.asm). Два экземпляра реальных структур сохраняют четыре и два исходных байта, массивы масок ещё шестнадцать. Начальная пара режима #0000 сохранена из образа, она не заменяется рабочим режимом до фактической подготовки вызывающим кодом.\n'
 inventory=read('Inventory');inventory['physical_bytes_by_kind']={kind:sum(v['length'] for v in source_map if v['kind']==kind) for kind in sorted({v['kind'] for v in source_map})};inventory['ranges_by_kind']=dict(collections.Counter(v['kind'] for v in source_map))
 for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+name+'.json')]=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 plan=[]
 for p,value in pending.items():
  data=value if isinstance(value,bytes) else value.encode('utf-8');rel=p.relative_to(ROOT);before=p.read_bytes() if p.exists() else None;target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);plan.append((rel,before,data))
 # Проверка текущих файлов и кандидата до применения, исходные снимки остаются в истории.
 for rel,before,data in plan:assert ((ROOT/rel).read_bytes()==before if before is not None else not (ROOT/rel).exists()) and (candidate/rel).read_bytes()==data
 for rel,before,data in plan:
  if before is not None:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
 for original in originals:target=history/original.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
 for rel,before,data in plan:target=ROOT/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 import importlib,VerifySources
 with contextlib.redirect_stdout(io.StringIO()):importlib.reload(VerifySources).main()
 for original in originals:
  assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==(history/original.relative_to(ROOT)).read_bytes();original.unlink()
 report=dict(passed=True,typed_bytes=22,physical_structures=2,physical_records=2,pixel_mask_bytes=16,original_initial_values_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewEdgeDataClassification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
