"""Поток EE34 доказан писателем 63D5 и реальным кадровым потребителем, шесть физических строк."""
from collections import Counter
import contextlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionAyStreams as facts


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    proof=read('ActionAyStreamPlaybackVerification');assert proof['streams']==8 and proof['physical_stream_bytes']==384 and proof['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();sm,symbols,inventory=[read(n) for n in ('SourceMap','Symbols','Inventory')]
    old=next(p for p in sm if p['slot']==17 and p['offset']==0x8E34);assert (old['kind'],old['length'])==('unclassified',25)
    old_path=ROOT/old['path'];assert old_path.read_bytes()==source[0x8E34:0x8E4D]
    streams=(('PairedAim',0xEE34,6),);path='Source/Action/Data/AyPairedAimStream.asm'
    text,labels=facts.render(source,streams);assert facts.parse(text,streams)==(source[0x8E34:0x8E4D],labels)
    assert not set(labels)&set(symbols);symbols.update(labels);pending={ROOT/path:text.encode('utf-8')}
    old.update(kind='typed_data',path=path,origin=0xEE34)
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm));inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory)):pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    current_path=ROOT/'Source/Files/17_ACTION.inc';current=current_path.read_text('utf-8');needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert current.count(needle)==1
    replacement='                disp #EE34\n                include "../Action/Data/AyPairedAimStream.asm"\n                ent'
    pending[current_path]=current.replace(needle,replacement).encode('utf-8')
    current_path=ROOT/'Tools/Disasm/Research/ActionAyStreams.py';current=current_path.read_text('utf-8')
    current=current.replace('Семь потоков','Восемь потоков')
    needle="('Capture',0xEE02,6),('FullSlots',0xEE1B,6))";assert current.count(needle)==1
    current=current.replace(needle,"('Capture',0xEE02,6),('FullSlots',0xEE1B,6),('PairedAim',0xEE34,6))")
    needle="('Source/Action/Data/AyCaptureStreams.asm',STREAMS[5:]))";assert current.count(needle)==1
    pending[current_path]=current.replace(needle,"('Source/Action/Data/AyCaptureStreams.asm',STREAMS[5:7]),\n        ('Source/Action/Data/AyPairedAimStream.asm',STREAMS[7:]))").encode('utf-8')
    current_path=ROOT/'Tools/Disasm/Research/CheckActionAyStreamPlayback.py';pending[current_path]=current_path.read_text('utf-8').replace('семи исходных потоков','восьми исходных потоков').encode('utf-8')
    current_path=ROOT/'Source/Action/RequestPairedAimLines.asm';current=current_path.read_text('utf-8');assert current.count('@ActionPairedAimConst.SoundCursor')==1
    pending[current_path]=current.replace('@ActionPairedAimConst.SoundCursor','@ActionAyStreams.PairedAimRow00').encode('utf-8')
    current_path=ROOT/'Tools/Disasm/Research/ActionPairedAimLinesFacts.py';current=current_path.read_text('utf-8')
    current=current.replace("'LD HL, @ActionPairedAimConst.SoundCursor'","'LD HL, @ActionAyStreams.PairedAimRow00'")
    current='\n'.join(line for line in current.splitlines() if not line.startswith('SoundCursor     equ #EE34'))+'\n';pending[current_path]=current.encode('utf-8')
    current_path=ROOT/'Includes/Const/Include.inc';current=current_path.read_text('utf-8');assert current.count('SoundCursor     equ #EE34')==1
    pending[current_path]=('\n'.join(line for line in current.splitlines() if not line.startswith('SoundCursor     equ #EE34'))+'\n').encode('utf-8')
    current_path=ROOT/'Docs/ActionAyStreams.md';current=current_path.read_text('utf-8')
    current=current.replace('# Физические строки семи потоков AY','# Физические строки восьми потоков AY')
    begin=current.index('Три файла ');end=current.index('\n\n',begin)
    intro='Четыре файла [AyStreamsFirst.asm](../Source/Action/Data/AyStreamsFirst.asm), [AyCaptureStreams.asm](../Source/Action/Data/AyCaptureStreams.asm), [AyPairedAimStream.asm](../Source/Action/Data/AyPairedAimStream.asm) и [AyStreamsLater.asm](../Source/Action/Data/AyStreamsLater.asm) содержат 94 физических экземпляра FActionAyFrame и восемь отдельных нулевых маркеров, всего 384 исходных байта ACTION банка 0. Читатель [UpdateAyEffects](../Source/Action/UpdateAyEffects.asm) описан [отдельно](ActionAyEffects.md).'
    current=current[:begin]+intro+current[end:]
    needle='| WaitLoopRow00';at=current.index(needle)
    row='| PairedAimRow00 | EE34 | 6 | EE4C | RequestPairedAimLines задаёт поток A после фазового допуска и расхода ThirdValue |\n'
    current=current[:at]+row+current[at:]
    begin=current.index('Первый файл занимает');end=current.index('\n\n',begin)
    current=current[:begin]+'Физические интервалы потоков занимают ED8F..EDC0, EE02..EE33, EE34..EE4C и EE4D..EF4F. Промежуток EDC1..EE01 сохранён как Unknown, его внешнее сходство с потоком не доказывает потребителя. С EF50 начинается отдельная типизированная таблица состояний и последующий код, они не относятся к звуковым строкам.'+current[end:]
    current=current.replace('42 последовательности и 570 вызовов','48 последовательностей и 612 вызовов')
    pending[current_path]=current.encode('utf-8')
    current_path=ROOT/'Docs/ActionAyEffects.md';pending[current_path]=current_path.read_text('utf-8').replace('Семь потоков с установленными границами','Восемь потоков с установленными границами').encode('utf-8')
    current_path=ROOT/'Docs/ActionPairedAimLines.md';current=current_path.read_text('utf-8')
    current+='\n[Поток PairedAim по EE34](../Source/Action/Data/AyPairedAimStream.asm) оформлен шестью физическими FActionAyFrame и отдельным нулевым маркером. Кадровое воспроизведение исходных байтов проверено в обоих каналах до отключения, слышимая длительность и реальный AY не проверялись.\n'
    pending[current_path]=current.encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionPairedAimStream';history=ROOT/'Tools/Disasm/Research/History/BeforeActionPairedAimStream'
    assert not candidate.exists() and not history.exists();plan=[(p,p.read_bytes() if p.exists() else None,a) for p,a in pending.items()]
    for current_path,before,after in plan:
        target=candidate/current_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for current_path,before,after in plan:assert current_path.read_bytes()==before if before is not None else not current_path.exists()
    for current_path,before,after in plan:
        if before is not None:
            target=history/current_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/old_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old_path.read_bytes())
    for current_path,before,after in plan:
        current_path.parent.mkdir(parents=True,exist_ok=True)
        if current_path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=current_path.parent,prefix='aim-stream-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,current_path)
        else:current_path.write_bytes(after)
    importlib.reload(facts)
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==source[0x8E34:0x8E4D]==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=25,physical_frames=6,streams=8,new_physical_symbols=len(labels),original_bytes_preserved=True,writer=0x63D5,playback_sequences=48,playback_ticks=612,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionPairedAimStreamClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
