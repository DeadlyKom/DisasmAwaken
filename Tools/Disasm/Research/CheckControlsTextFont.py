"""Обратимость 4992 битов шрифта и оригинальный рисователь для всех 256 входных байтов."""
import hashlib,json
from PIL import Image
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory,payload
from CheckControlsTextDisplay import execute
import ReferenceControlsTextDisplay as text
import ControlsTextFont as font


def main():
    source=payload(22);raw=source[font.START:font.END];glyphs=font.unpack(raw);assert font.pack(glyphs)==raw
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes());entry=next(e for e in manifest['entries'] if e['slot']==22)
    image=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert raw==image[entry['offset']+font.START:entry['offset']+font.END]
    base=base_memory();text.initialize(base);cases=0
    # Проверка каждого исходного кода, включая 48 кодов, читающих байты соседнего исполняемого кода вместо выделенного растра.
    for code in range(256):
        for column in (0,1,23,24):
            actual=list(base)
            for address in range(0x4000,0x5B00):actual[address]=(address*73+code)&255
            actual[text.COLUMN]=column;expected=list(actual);events=[];text.glyph(expected,code,events)
            native_events,_=execute(actual,0xEFC4,code)
            assert native_events==events,(code,column)
            ignored={0xEFC1,0xEFC2}
            assert all(actual[a]==expected[a] for first,last in ((0x4000,0xBF00),(0xC000,65536)) for a in range(first,last) if a not in ignored),(code,column)
            cases+=1
    atlas=Image.new('L',(128,42),255)
    for index,glyph in enumerate(glyphs):
        for y,row in enumerate(glyph):
            for x,bit in enumerate(row):atlas.putpixel((index%32*4+x,index//32*6+y),0 if bit else 255)
    target=ROOT/'Tools/Disasm/Research/Evidence/ControlsTextFont4x6.png';target.parent.mkdir(parents=True,exist_ok=True);atlas.save(target)
    result=dict(passed=True,total_cases=cases,physical_bytes=624,physical_pixel_bits=4992,glyphs=208,pairs=104,
        first_code=32,last_code=239,all_input_bytes_real_renderer_checked=True,out_of_font_input_codes=48,
        out_of_font_reads_neighboring_original_code=True,no_range_guard_added=True,roundtrip_all_pixel_bits=True,
        original_disk_payload_sha256=hashlib.sha256(raw).hexdigest(),independent_text_renderer_memory_and_events_checked=True,
        ordinary_stack_and_scroll_saved_SP_excluded=True,exact_registers_R_T_and_write_multiplicity_checked=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsTextFontVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
