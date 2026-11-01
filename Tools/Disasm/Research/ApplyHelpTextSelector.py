"""Договор одного существующего HELP-входа и однозначный банк его изменяемого байта."""
from pathlib import Path
import contextlib,io,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research')]
import HelpTextSelectorFacts as facts
from VerifySources import main as verify


def main():
 with contextlib.redirect_stdout(io.StringIO()):verify()
 def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
 def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 assert read('HelpTextSelectorVerification')['passed'];candidate=ROOT/'Tools/Disasm/Research/Candidates/HelpTextSelectorScoped';history=ROOT/'Tools/Disasm/Research/History/BeforeHelpTextSelector'
 assert not candidate.exists() and not history.exists();pending={};p=ROOT/'Source/Help/SelectText.asm'
 lines=['                module Help','                module SelectText','                ; Документация [номер LF-записи и единственный изменяемый байт банка 7](../../Docs/HelpTextSelector.md)',
  '                ; -----------------------------------------','                ; '+facts.FUNCTIONS[0xDB57][1],'                ; исходная запись 8, банк 7, файловые смещения #0057..#005A']
 for title,values in zip(('In','Out','Corrupt','Note'),facts.CONTRACTS['Help',0xDB57]):lines+=['                ; '+title+':']+['                ;   '+v for v in values]
 lines+=['                ; -----------------------------------------','                ; подготовка LF-записи, которую следующий индексатор прочитает своим LD A',
  'Entry:          LD (@HelpTextState.RecordOperand), A','                RET','','                endmodule','                endmodule'];pending[p]=('\n'.join(lines)+'\n').encode('utf-8')
 p=ROOT/'Includes/Variables/Include.inc';t=p.read_text('utf-8');assert 'module HelpTextState' not in t and t.count('                endif\n')==1
 block='                module HelpTextState\n'+('RecordOperand'.ljust(16)+'equ #DB01').ljust(80)+'; банк 7, байт номера LF-записи внутри LD A индексатора HELP\n                endmodule\n\n';pending[p]=t.replace('                endif\n',block+'                endif\n').encode('utf-8')
 for filename,extra in (
  ('Knowledge.py','\nfrom HelpTextSelectorFacts import FUNCTIONS as HELP_TEXT_SELECTOR_FUNCTIONS\nFUNCTIONS[\'Help\'].update(HELP_TEXT_SELECTOR_FUNCTIONS)\n'),
  ('Contracts.py','\nfrom HelpTextSelectorFacts import CONTRACTS as HELP_TEXT_SELECTOR_CONTRACTS\nCONTRACTS.update(HELP_TEXT_SELECTOR_CONTRACTS)\n'),
  ('SemanticNames.py','\nfrom HelpTextSelectorFacts import DOCUMENTS as HELP_TEXT_SELECTOR_DOCUMENTS, name_operands as help_text_selector_name_operands\nDOCUMENTS.update(HELP_TEXT_SELECTOR_DOCUMENTS)\n')):
  p=ROOT/'Tools/Disasm/Research'/filename;t=p.read_text('utf-8');assert 'from HelpTextSelectorFacts import' not in t
  if filename=='SemanticNames.py':
   needle='    operation = shipmodelactionsstation_name_operands(region, function_address, operation)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    operation = help_text_selector_name_operands(region, function_address, operation)')
  pending[p]=(t+extra).encode('utf-8')
 functions=read('Functions');f=next(f for f in functions if f['region']=='Help' and f['address']==0xDB57);f['description']=facts.FUNCTIONS[0xDB57][1];pending[ROOT/'Tools/Disasm/Reports/Functions.json']=encode(functions)
 modified=read('ModifiedCode');writer=next((v for v in modified if v['region']=='Help' and v['writer']==0xDB57),None)
 if writer is None:writer=dict(region='Help',writer=0xDB57,target=0xDB01,target_instruction=0xDB00,size=1,target_operation='LD A,#00',path='Source/Help/SelectText.asm');modified.append(writer)
 assert (writer['target'],writer['size'])==(0xDB01,1);writer.update(target_region='Help',writer_bank=7,target_bank=7,target_slot=8);pending[ROOT/'Tools/Disasm/Reports/ModifiedCode.json']=encode(modified)
 p=ROOT/'Docs/FunctionDetails/Help.md';t=p.read_text('utf-8');t+='\n[SelectText](../../Source/Help/SelectText.asm) теперь имеет [проверенный регистровый договор](../HelpTextSelector.md), все 65536 AF сохраняются, меняется только байт операнда DB01 в банке 7. Контракты остальных HELP-помощников этим результатом не закрываются.\n';pending[p]=t.encode('utf-8')
 if not any(v['region']=='Help' and v['writer']==0xDB57 for v in read('ModifiedCode')):
  p=ROOT/'Docs/ModifiedCode.md';t=p.read_text('utf-8');t+='\n| Help | #DB57 | #DB01 | банк 7, LD A,#00 | [SelectText.asm](../Source/Help/SelectText.asm) |\n';pending[p]=t.encode('utf-8')
 plan=[]
 for p,data in pending.items():
  rel=p.relative_to(ROOT);old=p.read_bytes();plan.append((rel,old,data));target=candidate/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 for rel,old,data in plan:assert (ROOT/rel).read_bytes()==old
 for rel,old,data in plan:target=history/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(old)
 for rel,old,data in plan:(ROOT/rel).write_bytes(data)
 with contextlib.redirect_stdout(io.StringIO()):verify()
 result=dict(passed=True,previously_named_contract_described=1,instructions_changed=0,bank_7_operand_explicit=True,physical_bytes_preserved=True,scoped_candidate_and_history=True,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpTextSelectorClassification.json').write_bytes(encode(result));print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
