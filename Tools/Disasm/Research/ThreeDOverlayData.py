"""Четыре физических блока отдельно собираемой копии, общие STRUCT без второй декларации."""
import re
from ActionClipProductsData import render as render_products,parse as parse_products
from ActionClipPointsData import render as render_point,parse as parse_point
from ActionLineMasksData import render as render_masks,parse as parse_masks

NAMES={'ActionClipProductsData':'ThreeDClipProductsData','ActionClipPoints':'ThreeDClipPoints','ActionLineMasks':'ThreeDLineMasks'}
TABLES=(('Source/ThreeD/Data/ClipFirstPoint.asm',0xF0B,0xF10),
        ('Source/ThreeD/Data/ClipSecondPoint.asm',0xF1B,0xF20),
        ('Source/ThreeD/Data/ClipProducts.asm',0xF2B,0xF3B),
        ('Source/ThreeD/Data/LineMasks.asm',0x2010,0x2020))


def rename(text,reverse=False):
    for old,new in NAMES.items():
        if reverse:old,new=new,old
        text=re.sub(r'\b'+old+r'\b',new,text)
    return text


def labels(names):
    return {rename(key):value for key,value in names.items()}


def render(source,path):
    dummy=bytes(0x6000)+bytes(source)
    if path.endswith('ClipProducts.asm'):text,names=render_products(dummy)
    elif path.endswith('LineMasks.asm'):text,names=render_masks(dummy)
    else:
        name,offset=('FirstPoint',0x6F0B) if path.endswith('ClipFirstPoint.asm') else ('SecondPoint',0x6F1B)
        text,names=render_point(dummy,name,offset)
    text=rename(text)
    text=re.sub(r'\]\((?:\.\./)+Docs/[^)]+\.md\)','](../../../Docs/ThreeDOverlayMirror.md)',text)
    return text,labels(names)


def parse(path,text):
    text=rename(text,True)
    if path.endswith('ClipProducts.asm'):raw,names=parse_products(text)
    elif path.endswith('LineMasks.asm'):raw,names=parse_masks(text)
    else:
        name,offset=('FirstPoint',0x6F0B) if path.endswith('ClipFirstPoint.asm') else ('SecondPoint',0x6F1B)
        raw,names=parse_point(text,name,offset)
    return raw,labels(names)


def verify_data(root,sources,source_map,symbols):
    found=[item for item in source_map if item['path'] in {row[0] for row in TABLES}]
    if not found:return
    assert len(found)==4
    for path,start,end in TABLES:
        raw,names=parse(path,(root/path).read_text('utf-8'))
        assert raw==sources[19][start:end]
        assert all(symbols.get(key.upper())==value for key,value in names.items())
        item=next(item for item in found if item['path']==path)
        assert (item['slot'],item['offset'],item['length'],item['origin'])==(19,start,end-start,0xC000+start)


def export_data(source,special,write,symbols):
    for path,start,end in TABLES:
        text,names=render(source,path);write(path,text);symbols.update(names)
        special[19,start]=(end,path,0xC000+start)
