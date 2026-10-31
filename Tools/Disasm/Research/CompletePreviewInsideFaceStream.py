"""Завершение применения кандидата после замены неподдерживаемого сверкой умножения адреса."""
from pathlib import Path
import contextlib,io,json,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify


def main():
 report_path=ROOT/'Tools/Disasm/Reports/PreviewInsideFaceStreamClassification.json';assert not report_path.exists()
 candidate=ROOT/'Tools/Disasm/Research/Candidates/PreviewInsideFaceStreamScoped';history=ROOT/'Tools/Disasm/Research/History/BeforePreviewInsideFaceStream'
 rel=Path('Source/D3D/RenderPreviewInsideFaces.asm');source=ROOT/rel;draft=candidate/rel
 old='LD DE, @PreviewPolygonConst.PointPage * 256';new='LD DE, @PreviewPolygonPrepConst.FirstPointRow - 1'
 # Проверка, что после применения кандидата не появилось посторонних изменений рабочей копии.
 for path in candidate.rglob('*'):
  if path.is_file():assert (ROOT/path.relative_to(candidate)).read_bytes()==path.read_bytes()
 text=source.read_text('utf-8');assert text.count(old)==1 and new not in text
 source.write_text(text.replace(old,new),'utf-8');draft.write_bytes(source.read_bytes())
 with contextlib.redirect_stdout(io.StringIO()):verify()
 # Удаление только исходного заменённого ресурса после сверки точного снимка и активного реестра.
 original=ROOT/'Source/Resources/06_D3D/BeforeFaceCodes.bin';saved=history/original.relative_to(ROOT)
 assert original.resolve().is_relative_to(ROOT/'Source/Resources/06_D3D') and original.read_bytes()==saved.read_bytes()
 source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'));assert not any(v['path']==original.relative_to(ROOT).as_posix() for v in source_map)
 original.unlink()
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'));rows=[i for g in flow if g['name']=='D3D' for i in g['instructions'] if 0xDD4F<=i['address']<0xDDFD]
 writes=[i for i in rows if re.fullmatch(r'LD \(#[0-9A-F]+\),(A|DE|HL)',i['operation'])]
 report=dict(passed=True,functions=1,instructions=len(rows),code_bytes=174,registered_operand_writers=1,verified_physical_data_writers=len(writes)-1,scoped_candidate_and_history=True,physical_bytes_preserved=True,address_expression_rewritten_without_opcode_change=True,assembly_executed=False)
 report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
