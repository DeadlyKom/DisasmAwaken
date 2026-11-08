"""Публикация восемнадцати исходных байтов базиса и именование действительных потребителей."""
from collections import Counter
import contextlib,importlib,io,json,os,sys,tempfile
from CheckIntro import ROOT
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from VerifySources import main as verify
import ActionRenderBasisData as facts


def main():
    def read(stem):return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):verify()
    assert read('ActionBankedBasisRotationVerification')['passed']
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    start,end=facts.TABLE[2:4];original=source[start:end]
    assert [int.from_bytes(original[i:i+2],'little') for i in range(0,18,2)]==[32767,0,0,0,32767,0,0,0,32767]
    sm,symbols,inventory,modified=[read(n) for n in ('SourceMap','Symbols','Inventory','ModifiedCode')]
    old=next(p for p in sm if p['slot']==17 and p['offset']==start)
    assert old['kind']=='unclassified' and old['length']==18
    old_path=ROOT/old['path'];assert old_path.read_bytes()==original
    pending={};text,labels=facts.render(source);assert facts.parse(text)==(original,labels)
    assert not set(labels)&set(symbols);symbols.update(labels);pending[ROOT/facts.TABLE[1]]=text.encode('utf-8')
    old.update(kind='typed_data',path=facts.TABLE[1],origin=0x9B00)
    inventory['ranges_by_kind']=dict(Counter(p['kind'] for p in sm))
    inventory['physical_bytes_by_kind']={k:sum(p['length'] for p in sm if p['kind']==k) for k in inventory['ranges_by_kind']}
    for item in modified:
        if item.get('target_path')==str(old_path.relative_to(ROOT)).replace('\\','/'):
            assert item['target_slot']==17 and start<=item['target_offset']<end
            item.update(target_path=facts.TABLE[1],target_source_classified=True)
    for stem,value in (('SourceMap',sm),('Symbols',symbols),('Inventory',inventory),('ModifiedCode',modified)):
        pending[ROOT/('Tools/Disasm/Reports/'+stem+'.json')]=encode(value)
    path=ROOT/'Source/Files/17_ACTION.inc';text=path.read_text('utf-8')
    needle='                incbin "../Resources/17_ACTION/'+old_path.name+'"';assert text.count(needle)==1
    pending[path]=text.replace(needle,'                disp #9B00\n                include "../Action/Data/RenderBasis.asm"\n                ent').encode('utf-8')
    path=ROOT/'Includes/Structs/Include.inc';text=path.read_text('utf-8');assert 'struct FBasisWord' not in text
    pending[path]=text.replace('                endif',facts.structure()+'\n                endif').encode('utf-8')
    # Именование только двух установленных потребителей, числовые инструкции и страницы не меняются.
    changes=0
    for relative,region,address in (('Source/Action/RenderSceneFrame.asm','Action',0xE020),
                                    ('Source/Voxel/RotateBasisVectors.asm','Voxel',0xE500)):
        path=ROOT/relative;text=path.read_text('utf-8');lines=[]
        for line in text.splitlines():
            code,sep,note=line.partition(';');after=facts.name_operands(region,address,code)
            if after!=code:
                changes+=1
                line=after.rstrip().ljust(80)+';'+note if sep else after
            lines.append(line)
        pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    assert changes>=45
    path=ROOT/'Tools/Disasm/Research/SemanticNames.py';text=path.read_text('utf-8')
    needle='    operation = ship_preview_callback_name_operands(region, function_address, operation)';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    operation = action_render_basis_name_operands(region,function_address,operation)')
    pending[path]=(text+'\nfrom ActionRenderBasisData import name_operands as action_render_basis_name_operands\n').encode('utf-8')
    path=ROOT/'Tools/Disasm/VerifySources.py';text=path.read_text('utf-8')
    needle='    # Проверка физических десяти исходных пропусков и завершающего кода списка.';assert text.count(needle)==1
    hook='''    # Проверка девяти физических слов базиса и их двух байтовых полей.
    from ActionRenderBasisData import TABLE as RENDER_BASIS_TABLE, parse as parse_render_basis
    raw,labels=parse_render_basis((ROOT/RENDER_BASIS_TABLE[1]).read_text('utf-8'))
    assert raw==sources[17][0x3B00:0x3B12]
    assert all(symbols.get(k.upper())==v for k,v in labels.items())
    assert symbols['FBASISWORD']==2 and symbols['FBASISWORD.LOW']==0 and symbols['FBASISWORD.HIGH']==1
    rows=[p for p in source_map if p['path']==RENDER_BASIS_TABLE[1]]
    assert len(rows)==1 and (rows[0]['offset'],rows[0]['length'],rows[0]['origin'])==(0x3B00,18,0x9B00)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/ExportSources.py';text=path.read_text('utf-8')
    needle='    token_text, token_records = render_token_tables(language, names)';assert text.count(needle)==1
    hook='''    # Физические слова базиса, исходные значения не заменяются расчётной матрицей.
    from ActionRenderBasisData import TABLE as RENDER_BASIS_TABLE, render as render_basis
    basis_text,basis_labels=render_basis(data_by_slot[17])
    write(RENDER_BASIS_TABLE[1],basis_text);symbols.update(basis_labels)
    special[17,0x3B00]=(0x3B12,RENDER_BASIS_TABLE[1],0x9B00)

'''
    pending[path]=text.replace(needle,hook+needle).encode('utf-8')
    # Обратные ссылки в действительных исходниках и их фабриках комментариев.
    path=ROOT/'Source/Voxel/RotateBasisVectors.asm';text=pending[path].decode('utf-8')
    needle='                ; проверка первого угла перед изменением первой и второй компонент трёх векторов';assert text.count(needle)==1
    pending[path]=text.replace(needle,'                ; Физические слова [базис](../../Docs/ActionRenderBasis.md)\n'+needle).encode('utf-8')
    path=ROOT/'Tools/Disasm/Research/EffectsNotes.py';text=path.read_text('utf-8')
    needle='0xE500: (["проверка первого угла';assert text.count(needle)==1
    pending[path]=text.replace(needle,'0xE500: (["Физические слова [базис](../../Docs/ActionRenderBasis.md)", "проверка первого угла').encode('utf-8')
    path=ROOT/'Docs/ActionRenderFrameSetup.md'
    pending[path]=(path.read_text('utf-8')+'\n[Физические слова базиса](ActionRenderBasis.md) оформлены FBasisWord по исходным восемнадцати байтам. Старшие байты имеют доказанное соответствие C00..C22, математическая нормировка этим не устанавливается.\n').encode('utf-8')
    candidate=ROOT/'Tools/Disasm/Research/Candidates/ActionRenderBasisData';history=ROOT/'Tools/Disasm/Research/History/BeforeActionRenderBasisData'
    assert not candidate.exists() and not history.exists()
    plan=[(p,p.read_bytes() if p.exists() else None,data) for p,data in pending.items()]
    for path,before,after in plan:
        target=candidate/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(after)
    for path,before,after in plan:assert path.read_bytes()==before if before is not None else not path.exists()
    for path,before,after in plan:
        if before is not None:
            target=history/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
    target=history/old_path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original)
    for path,before,after in plan:
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.json':
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='render-basis-',suffix='.tmp',delete=False) as output:
                temporary=output.name;output.write(after)
            os.replace(temporary,path)
        else:path.write_bytes(after)
    with contextlib.redirect_stdout(io.StringIO()):importlib.reload(sys.modules['VerifySources']).main()
    assert old_path.resolve().is_relative_to((ROOT/'Source/Resources/17_ACTION').resolve())
    assert old_path.read_bytes()==original==(history/old_path.relative_to(ROOT)).read_bytes();old_path.unlink()
    result=dict(passed=True,typed_bytes=18,physical_word_records=9,new_physical_symbols=len(labels),
        named_operand_sites=changes,original_bytes_and_instructions_preserved=True,
        orthonormality_or_pure_rotation_proved=False,input_IY_dependency_preserved=True,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRenderBasisDataClassification.json').write_bytes(encode(result));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
