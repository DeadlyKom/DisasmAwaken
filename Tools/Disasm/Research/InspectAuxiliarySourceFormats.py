"""Проверка нескольких форматов исходников, контроль на настоящем удалённом ALASM-файле."""
import hashlib,json,os,tempfile
from CheckIntro import ROOT

SIGNATURE=bytes.fromhex('f3 76 c7 dd fd ed b0 d9')
FORMAT_REFERENCE='https://github.com/Bedazzle/ZX-M8XXX/blob/main/core/asm-detok.js'
MNEMONICS=('INCLUDE INCBIN MACRO LOCAL RLCA RRCA HALT CALL PUSH RETN RETI DJNZ OUTI OUTD LDIR CPIR '
    'INIR OTIR LDDR CPDR INDR OTDR DD DEFB DEFW DEFS DISP ENDM EDUP ENDL MAIN ELSE DISPLAY EXA DB DW DS NOP '
    'INC DEC RLA RRA DAA CPL SCF CCF ADD ADC SUB SBC AND XOR RET POP RST EXX RLC RRC SLA SRA SLI SRL BIT RES '
    'SET OUT NEG RRD RLD LDI CPI INI LDD CPD IND ORG EQU ENT INF DUP IFN REPEAT UNTIL IF LD JR JP OR CP EX '
    'DI EI IN RL RR IM ENDIF EXD JNZ JZ JNC JC').split()
REGISTERS='BC DE HL AF IX IY SP NZ NC PO PE HX LX HY LY B C D E H L A P M Z R I'.split()


def alasm_view(data):
    signature=data.find(SIGNATURE)
    assert signature>=0
    position=signature+24;lines=[];frames=[]
    while position<len(data):
        start=position;length=data[position];position+=1
        if length==0:return '\n'.join(lines)+'\n',frames,position
        end=position+length-1;assert end<=len(data)
        raw=data[position:end];position=end
        frames.append(dict(offset=start,length=length,hex=data[start:end].hex()))
        text='';first=True;comment=False;quoted=False
        for value in raw:
            if comment:
                if value>=32:text+=bytes((value,)).decode('cp866')
            elif quoted:
                text+=bytes((value,)).decode('cp866')
                if value==34:quoted=False
            elif value==34:text+='"';quoted=True
            elif value==59:text+=';';comment=True
            elif value==16:comment=True
            elif value<16:text+=' '*value
            elif value>=128:
                if first:
                    assert value-128<len(MNEMONICS)
                    first=False;text=text.rstrip().ljust(16)+MNEMONICS[value-128]+' '
                elif 224<=value<=250:text+=REGISTERS[value-224]
                elif 159<=value<=164:text+=('(BC)','(DE)','(HL)','(SP)','(IX)','(IY)')[value-159]
                elif 208<=value<=211:text+=('(C)','(IX','(IY',"AF'")[value-208]
                else:assert value==255,('unsupported operand token',value)
            elif value==44:text+=', '
            else:text+=chr(value)
        assert not quoted
        lines.append(text.rstrip())
    raise AssertionError('ALASM source terminator missing')


def tasm_prefix(data):
    position=lines=0
    while position<len(data):
        length=data[position]
        if length==255:return dict(complete_lines=lines,terminator=True,stop_offset=position)
        end=position+length+1
        if end>=len(data) or data[end]!=length:break
        position=end+1;lines+=1
    return dict(complete_lines=lines,terminator=False,stop_offset=position)


def ads_prefix(data):
    position=lines=0;previous=-1
    while position+2<len(data):
        number=int.from_bytes(data[position:position+2],'little')
        if number in (0,65535):return dict(complete_lines=lines,terminator=True,stop_offset=position)
        if number<=previous:break
        end=data.find(b'\0',position+2)
        if end<0 or end-position-2>240:break
        previous=number;position=end+1;lines+=1
    return dict(complete_lines=lines,terminator=False,stop_offset=position)


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entries={entry['slot']:entry for entry in manifest['entries']}
    payloads={slot:(ROOT/(entry['path']+'.bin')).read_bytes() for slot,entry in entries.items()}
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    for slot,data in payloads.items():assert data==original[entries[slot]['offset']:entries[slot]['offset']+len(data)]
    # Проверка формата на реальном контрольном файле, а не только отрицательные эвристики BANK.
    control=payloads[2];assert entries[2]['deleted'] and control[:9]==b'HL->TXT H' and control.find(SIGNATURE)==40
    view,frames,end=alasm_view(control)
    assert end==len(control)==521 and control[end-1]==0
    reconstructed=control[:64]+b''.join(bytes.fromhex(row['hex']) for row in frames)+b'\0'
    assert reconstructed==control
    for name in ('DES_TXT','WYCHET','WCH1','WYCH1','WYCH2','NCH','DCH'):assert name in view
    assert all(('LD DE, '+value) in view for value in ('10000','1000','100','10'))
    assert 'число, которое необходимо перевести в TXT' in view
    banks=[]
    for slot in range(33,39):
        data=payloads[slot];signatures=[];position=0
        while (position:=data.find(SIGNATURE,position))>=0:signatures.append(position);position+=1
        tasm,ads=tasm_prefix(data),ads_prefix(data)
        assert not signatures and tasm['complete_lines']==0 and ads['complete_lines']<4
        banks.append(dict(slot=slot,name=entries[slot]['name'],sha256=hashlib.sha256(data).hexdigest(),
            alasm_signature_offsets=signatures,tasm_from_offset_zero=tasm,ads_from_offset_zero=ads))
    evidence='Tools/Disasm/Research/Evidence/DeletedDecimalFormatter.asm.txt'
    text=('; Исследовательское представление удалённого ALASM-файла, не исходник обычной сборки\n'
          '; Метки и авторские комментарии восстановлены из токенов, исходный каталог не меняется\n'+view)
    p=ROOT/evidence
    if p.exists():assert p.read_bytes()==text.encode('utf-8')
    else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode('utf-8'))
    result=dict(passed=True,format_reference=FORMAT_REFERENCE,
        positive_control=dict(slot=2,deleted=True,extracted=entries[2]['path']+'.bin',bytes=521,
            embedded_source_name='HL->TXT',alasm_signature_offset=40,first_line_offset=64,
            framed_lines=len(frames),source_terminator_end=end,all_native_source_frames_roundtrip=True,
            sha256=hashlib.sha256(control).hexdigest(),text_view=evidence,
            purpose='decimal number formatter, author input HL number and BC text destination'),
        banks=banks,recognized_native_bank_sources=False,
        arbitrary_offsets_fragmented_compressed_and_other_formats_excluded=False,
        banks_semantically_classified=False,deleted_catalog_entry_restored=False,
        ordinary_build_sources_changed=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/AuxiliarySourceFormatInspection.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='source-formats-',suffix='.tmp',delete=False) as out:
        temporary=out.name;out.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target)
    print(json.dumps(dict(passed=True,positive_control_lines=len(frames),positive_control_bytes=len(control),
        native_source_frames_roundtrip=True,banks_checked=len(banks),bank_formats_established=False),indent=2))


if __name__=='__main__':main()
