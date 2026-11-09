"""Проверка каждого бита графического ресурса scene1po, без предположения о его игровом загрузчике."""
import hashlib,json,os,tempfile
from PIL import Image,ImageDraw
from CheckIntro import ROOT
import Scene1PixelPairs as facts


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry=next(e for e in manifest['entries'] if e['slot']==facts.SLOT)
    data=(ROOT/(entry['path']+'.bin')).read_bytes()
    allocated=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert entry['length']==len(data)==facts.LOGICAL_BYTES and len(allocated)==18688
    assert allocated==original[entry['offset']:entry['offset']+len(allocated)] and allocated[:len(data)]==data
    planes=facts.unpack(data)
    assert facts.pack(planes)==data
    # Независимая адресация каждого пиксельного бита, а не только обратное применение того же прохода.
    for plane in range(2):
        for pixel,value in enumerate(planes[plane]):
            y,x=divmod(pixel,facts.WIDTH)
            offset=92*y+2*(x//8)+plane
            assert value==int(bool(data[offset]&(128>>(x&7))))
    assert planes[0][:8]==bytes((1,0,0,1,0,0,0,0)) and planes[1][:8]==bytes(8)
    # Сохранение отдельного исследовательского вида, палитра и смешивание не выдаются за игровой вывод.
    preview=Image.new('RGB',(facts.WIDTH,3*(facts.HEIGHT+18)),'white');draw=ImageDraw.Draw(preview)
    for plane in range(2):
        image=Image.frombytes('L',(facts.WIDTH,facts.HEIGHT),bytes(255*(1-bit) for bit in planes[plane]))
        y=plane*(facts.HEIGHT+18);draw.text((0,y),'Plane '+str(plane)+' - display convention 0=white 1=black',fill='black')
        preview.paste(image,(0,y+18))
    y=2*(facts.HEIGHT+18);draw.text((0,y),'Equal-weight average - research preview only',fill='black')
    values=bytes((255,128,0)[a+b] for a,b in zip(*planes))
    preview.paste(Image.frombytes('L',(facts.WIDTH,facts.HEIGHT),values),(0,y+18))
    path=ROOT/'Tools/Disasm/Research/Evidence/Scene1PixelPlanes.png'
    if path.exists():assert Image.open(path).convert('RGB').tobytes()==preview.tobytes()
    else:path.parent.mkdir(parents=True,exist_ok=True);preview.save(path)
    published=(ROOT/facts.PATH).is_file()
    if published:
        assert (ROOT/facts.PATH).read_bytes()==data and (ROOT/facts.TAIL_PATH).read_bytes()==allocated[len(data):]
    result=dict(passed=True,logical_bytes=len(data),allocated_bytes=len(allocated),sector_tail_bytes=len(allocated)-len(data),
        interpreted_width=facts.WIDTH,interpreted_height=facts.HEIGHT,byte_columns=facts.ROW_BYTES,
        interpreted_planes=2,pixel_bits_independently_checked=2*facts.WIDTH*facts.HEIGHT,
        all_bytes_roundtrip=True,sha256=hashlib.sha256(data).hexdigest(),published_source_checked=published,
        geometry_inferred_from_coherent_raster_and_byte_periodicity=True,geometry_from_runtime_metadata=False,
        runtime_loader_proved=False,runtime_palette_proved=False,runtime_plane_combination_proved=False,
        mask_pixel_format_asserted=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/Scene1PixelPairsVerification.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='scene-pixels-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
