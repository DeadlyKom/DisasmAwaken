"""Оформление только доказанной физической роли суффиксов, потребители и писатели остаются отдельным вопросом."""
from collections import Counter
import contextlib,hashlib,importlib,io,json,sys
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):verify()
    reports=ROOT/'Tools/Disasm/Reports';read=lambda name:json.loads((reports/(name+'.json')).read_bytes())
    encode=lambda value:(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    proof=read('AllocatedSectorSuffixInspection');assert proof['passed'] and proof['physical_suffix_bytes']==2558
    assert proof['source_map_sha256']==hashlib.sha256((reports/'SourceMap.json').read_bytes()).hexdigest()
    sm,inventory,modified=read('SourceMap'),read('Inventory'),read('ModifiedCode');pending={};remove={};ranges=[];renames={};file_texts={}
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes());entries={e['slot']:e for e in manifest['entries']}
    for evidence in proof['records']:
        slot=evidence['slot'];old=next(r for r in sm if r['path']==evidence['old_path']);old_path=ROOT/old['path'];raw=old_path.read_bytes()
        assert old['kind']=='unclassified' and old['offset']==evidence['old_offset'] and old['length']==evidence['old_length']
        assert not any(r.get('target_path')==old['path'] for r in modified)
        start=evidence['suffix_offset'];end=start+evidence['suffix_length'];prefix=start-old['offset'];suffix=raw[prefix:]
        assert hashlib.sha256(suffix).hexdigest()==evidence['suffix_sha256']
        if prefix or old_path.name.startswith('Unclassified'):
            new=old_path.parent.relative_to(ROOT).as_posix()+'/SectorTail.bin';assert not (ROOT/new).exists();pending[ROOT/new]=suffix
        else:new=old['path']
        if prefix:
            before=dict(old);before.update(length=prefix,sha256=hashlib.sha256(raw[:prefix]).hexdigest());pending[old_path]=raw[:prefix]
            pieces=[before]
        else:
            pieces=[]
            if new!=old['path']:remove[old_path]=raw;renames[old['path']]=new
        pieces.append(dict(slot=slot,offset=start,length=end-start,kind='binary_resource',path=new,origin=None,
            format='ORIGINAL_ALLOCATED_SECTOR_SUFFIX',sha256=hashlib.sha256(suffix).hexdigest()))
        sm[sm.index(old):sm.index(old)+1]=pieces
        ranges.append((slot,start,end,new,evidence['declared_length']))
        file=ROOT/('Source/Files/'+format(slot,'02d')+'_'+entries[slot]['name']+'.inc')
        text=file_texts.get(file,file.read_text('utf-8'));needle='                incbin "../'+old['path'][7:]+'"';assert text.count(needle)==1
        lines=[]
        if prefix:lines += [needle,'                assert $ == #'+format(start,'04X')]
        lines += ['                ; Физический суффикс выделенных секторов, неиспользуемость не установлена',
          '                ; Документация [границы и сохранение суффиксов](../../Docs/AllocatedSectorSuffixes.md)',
          '                incbin "../'+new[7:]+'"']
        file_texts[file]=text.replace(needle,'\n'.join(lines))
    pending.update({p:s.encode('utf-8') for p,s in file_texts.items()})
    inventory['ranges_by_kind']=dict(Counter(r['kind'] for r in sm));inventory['physical_bytes_by_kind']={k:sum(r['length'] for r in sm if r['kind']==k) for k in inventory['ranges_by_kind']}
    pending[reports/'SourceMap.json']=encode(sm);pending[reports/'Inventory.json']=encode(inventory)
    helper='"""Физические суффиксы выделенных секторов, игровая неиспользуемость не утверждается."""\nRANGES='+repr(tuple(ranges))+'\n'
    pending[ROOT/'Tools/Disasm/Research/AllocatedSectorSuffixResources.py']=helper.encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8');needle='    binary_resources[7, 0x2900]';assert text.count(needle)==1
    text=text.replace(needle,'    # Все байты выделенных суффиксов сохраняются, BASIC с машинными модулями исключён.\n    from AllocatedSectorSuffixResources import RANGES as ALLOCATED_SUFFIX_RANGES\n    for slot,start,end,path,declared in ALLOCATED_SUFFIX_RANGES:binary_resources[slot,start]=(end,path,"ORIGINAL_ALLOCATED_SECTOR_SUFFIX")\n'+needle)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle="(scene1.LOGICAL_BYTES,12,'unclassified',scene1.TAIL_PATH)";assert text.count(needle)==1
    text=text.replace(needle,"(scene1.LOGICAL_BYTES,12,'binary_resource',scene1.TAIL_PATH)")
    needle='    code_count = 0';assert text.count(needle)==1
    hook='''    # Проверка физической роли выделенных суффиксов, чтение игрой не исключается.
    from AllocatedSectorSuffixResources import RANGES as ALLOCATED_SUFFIX_RANGES
    for slot,start,end,path,declared in ALLOCATED_SUFFIX_RANGES:
        assert slot!=3 and start>=declared
        assert (ROOT/path).read_bytes()==sources[slot][start:end]
        rows=[r for r in source_map if r['path']==path]
        assert len(rows)==1 and (rows[0]['slot'],rows[0]['offset'],rows[0]['length'],rows[0]['kind'])==(slot,start,end-start,'binary_resource')
        assert rows[0]['format']=='ORIGINAL_ALLOCATED_SECTOR_SUFFIX'

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ControlsFlightMessages.py';text=path.read_text('utf-8')
    for old,new in renames.items():text=text.replace(old,new)
    pending[path]=text.encode('utf-8')
    lines=['# Физические суффиксы выделенных секторов','',
      '[Проверка происхождения](../Tools/Disasm/Research/InspectAllocatedSectorSuffixes.py), [первичный реестр](../Tools/Disasm/Reports/AllocatedSectorSuffixInspection.json), [текущие диапазоны](../Tools/Disasm/Research/AllocatedSectorSuffixResources.py).','',
      '16 диапазонов, 2558 байтов, находятся после объявленной длины соответствующих небейсиковых файлов и внутри выделенных им секторов. Это положительно установленная физическая роль. Содержимое всех байтов, включая повторяющийся текст и нули, сохраняется буквально. Термины «неиспользуемый», «мусор», «свободная память» к ним не применяются. Чтение TR-DOS полными секторами, прямое секторное чтение и последующие обращения игры этой классификацией не исключаются.','',
      'BASIC-файл AWAKEN исключён. За его объявленной длиной находятся подтверждённые машинные модули вступления, поэтому общий вывод о роли всех байтов после поля Length был бы ошибкой. Длина каталога и доказанный исполняемый состав не смешиваются.','',
      'У OBJECT3D и FINALF прежний неизвестный диапазон пересекал логическую границу. Неизвестная часть внутри длины остаётся отдельной и не классифицируется по роли последующего суффикса. Все физические смещения и порядок включений сохранены.','',
      '| Слот | Начало суффикса | Байтов | Исходный ресурс |','| --- | --- | --- | --- |']
    for slot,start,end,path,declared in ranges:lines.append('| '+str(slot)+' | '+format(start,'04X')+' | '+str(end-start)+' | ['+entries[slot]['name']+'](../'+path+') |')
    lines+=['','VerifySources проверяет каждый текущий ресурс по извлечённым физическим секторам, его SourceMap, начало после объявленной длины и полный набор байтов. Публикация предварительно сверяет оригинальный TRD, длины и SHA256. Сборка и нативный запуск не выполнялись. Эта физическая классификация не является полным смысловым разбором возможных игровых потребителей.']
    pending[ROOT/'Docs/AllocatedSectorSuffixes.md']=('\n'.join(lines)+'\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/AllocatedSectorSuffixes';history=ROOT/'Tools/Disasm/Research/History/BeforeAllocatedSectorSuffixes';assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,after) for p,after in pending.items()]
    for p,before,after in plan:
        q=candidate/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(after)
    for p,before,after in plan:assert p.read_bytes()==before if before is not None else not p.exists()
    for p,before in {**{p:b for p,b,_ in plan if b is not None},**remove}.items():
        q=history/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before)
    for p,before,after in plan:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    for path,raw in remove.items():
        assert path.resolve().is_relative_to((ROOT/'Source/Resources').resolve()) and path.read_bytes()==raw==(history/path.relative_to(ROOT)).read_bytes();path.unlink()
    result=dict(passed=True,physical_suffix_ranges=16,physical_suffix_bytes=2558,basic_after_length_bytes_not_reclassified=True,
        logical_unknown_prefixes_preserved=2,all_original_bytes_offsets_and_instructions_preserved=True,
        live_consumers_and_writers_not_proved=True,unused_not_assumed=True,assembly_executed=False,native_execution=False)
    (reports/'AllocatedSectorSuffixClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
