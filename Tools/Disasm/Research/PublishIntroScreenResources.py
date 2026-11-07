"""Выделение двух доказанных экранов и сохранение неизвестного физического хвоста."""
from collections import Counter
import contextlib
import hashlib
import io
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
from CheckIntro import ROOT
from IntroScreenResources import BITMAP, ATTRIBUTES, PACKED, TAIL, render_attributes, parse_attributes
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    load = lambda name: json.loads((reports/(name+'.json')).read_text('utf-8'))
    assert load('IntroScreenResourcesVerification')['passed']
    source_map, symbols, inventory = (load(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    source = (ROOT/'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    old_screen = next(row for row in source_map if row['slot']==3 and row['offset']==0xB31)
    old_packed = next(row for row in source_map if row['slot']==3 and row['offset']==0x26CB)
    assert old_screen['kind']==old_packed['kind']=='unclassified'
    assert old_screen['length']==6912 and old_packed['length']==1589
    text, labels = render_attributes(source[0x2331:0x2631])
    assert parse_attributes(text)==source[0x2331:0x2631]
    pending = {ROOT/BITMAP:source[0xB31:0x2331], ROOT/ATTRIBUTES:text.encode('utf-8'),
               ROOT/PACKED:source[0x26CB:0x2C6B], ROOT/TAIL:source[0x2C6B:0x2D00]}
    def record(old, offset, length, path, kind, origin):
        return dict(old, offset=offset, length=length, path=path, kind=kind, origin=origin,
                    sha256=hashlib.sha256(source[offset:offset+length]).hexdigest())
    index=source_map.index(old_screen)
    source_map[index:index+1]=[record(old_screen,0xB31,6144,BITMAP,'resource',0x6E31),
                              record(old_screen,0x2331,768,ATTRIBUTES,'typed_data',0x8631)]
    index=source_map.index(old_packed)
    source_map[index:index+1]=[record(old_packed,0x26CB,1440,PACKED,'binary_resource',0x6ECB),
                              record(old_packed,0x2C6B,149,TAIL,'unclassified',None)]
    for key,value in labels.items():
        assert key not in symbols
        symbols[key]=value
    path=ROOT/'Source/Files/03_AWAKEN.inc'
    text=path.read_text('utf-8')
    old='                incbin "../Resources/03_AWAKEN/Unclassified009.bin"'
    assert text.count(old)==1
    text=text.replace(old, '''                ; Начальный экран до переноса распаковщика, 6144 bitmap и 768 атрибутов.
                incbin "../Intro/Data/InitialScreenBitmap.bin"
                assert $ == #2331
                disp #8631
                include "../Intro/Data/InitialScreenAttributes.asm"
                ent''')
    old='                incbin "../Resources/03_AWAKEN/Unclassified010.bin"'
    assert text.count(old)==1
    text=text.replace(old, '''                ; Поток после кода распаковщика, он переносится по адресу 6ECB.
                incbin "../Intro/Data/StationScreenPacked.bin"
                assert $ == #2C6B
                ; Следующие 149 байтов не читаются установленным экранным потоком.
                incbin "../Resources/03_AWAKEN/UnknownAfterStationScreen.bin"''')
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                disp #', '                disp #')
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                ; Начальный экран', '                ; Начальный экран')
    text=text.replace('                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                ; Поток после', '                ; Поток после')
    pending[path]=text.encode('utf-8')
    path=ROOT/'Source/Intro/InitializeIntro.asm'
    text=path.read_text('utf-8')
    old=';   исходная запись вступления размещена по #6300, экран и рабочие банки доступны'
    assert text.count(old)==1
    text=text.replace(old,';   загружены 44 сектора по #6400..#8FFF из файлового смещения #0100, экран и рабочие банки доступны')
    text=text.replace('                module InitializeIntro',
                      '                module InitializeIntro\n                ; Физические данные [два экранных ресурса](../../Docs/IntroScreenResources.md)',1)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Source/IntroUnpack/UnpackScreen.asm'
    text=path.read_text('utf-8').replace('                module UnpackScreen',
        '                module UnpackScreen\n                ; Исходный поток [экранные ресурсы](../../Docs/IntroScreenResources.md)',1)
    pending[path]=text.encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py'
    text=path.read_text('utf-8')
    marker='    # Проверка двух физических экранов выбора, без предположения об их загрузке.'
    assert text.count(marker)==1
    hook='''    # Проверка исходного bitmap вступления, физических строк атрибутов и всего прочитанного упакованного потока.
    from IntroScreenResources import BITMAP as intro_bitmap, ATTRIBUTES as intro_attributes
    from IntroScreenResources import PACKED as intro_packed, TAIL as intro_screen_tail
    from IntroScreenResources import parse_attributes as parse_intro_attributes, render_attributes as render_intro_attributes
    assert (ROOT/intro_bitmap).read_bytes()==sources[3][0xB31:0x2331]
    assert parse_intro_attributes((ROOT/intro_attributes).read_text('utf-8'))==sources[3][0x2331:0x2631]
    _, intro_screen_labels=render_intro_attributes(sources[3][0x2331:0x2631])
    assert all(symbols[key.upper()]==value for key,value in intro_screen_labels.items())
    assert (ROOT/intro_packed).read_bytes()==sources[3][0x26CB:0x2C6B]
    assert (ROOT/intro_screen_tail).read_bytes()==sources[3][0x2C6B:0x2D00]

'''
    pending[path]=text.replace(marker,hook+marker).encode('utf-8')
    inventory['ranges_by_kind']=dict(Counter(row['kind'] for row in source_map))
    totals=Counter()
    for row in source_map:
        totals[row['kind']]+=row['length']
    inventory['physical_bytes_by_kind']=dict(totals)
    for name,value in (('SourceMap',source_map),('Symbols',symbols),('Inventory',inventory)):
        pending[reports/(name+'.json')]=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    removed=[ROOT/old_screen['path'],ROOT/old_packed['path']]
    candidate=ROOT/'Tools/Disasm/Research/Candidates/IntroScreenResources'
    history=ROOT/'Tools/Disasm/Research/History/BeforeIntroScreenResources'
    assert not candidate.exists() and not history.exists()
    before={path:path.read_bytes() if path.exists() else None for path in (*pending,*removed)}
    for path,raw in pending.items():
        target=candidate/path.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
    # Проверка исходной рабочей копии перед заменой, история не заменяет непроверенные пользовательские изменения.
    for path,raw in before.items():
        assert path.read_bytes()==raw if raw is not None else not path.exists()
        if raw is not None:
            target=history/path.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
    for path,raw in pending.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='intro-screen-',suffix='.tmp',delete=False) as output:
                temporary=Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary,path)
            finally:
                if temporary.exists():temporary.unlink()
        else:path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        importlib.reload(sys.modules['VerifySources']).main()
    for path in removed:
        assert path.resolve().is_relative_to((ROOT/'Source/Resources').resolve())
        assert path.read_bytes()==(history/path.relative_to(ROOT)).read_bytes()
        path.unlink()
    print('6912 байтов начального экрана и 1440 байтов потока выделены, хвост 149 байтов сохранён Unknown')


if __name__=='__main__':main()
