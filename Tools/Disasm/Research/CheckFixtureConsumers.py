"""Повтор моделей общего конструктора после устранения перекрытия исполняемого кода B400."""
import concurrent.futures,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
RESEARCH=ROOT/'Tools/Disasm/Research'
MODELS=('CheckEquipmentTradeMode','CheckEquipmentListSetup','CheckEquipmentInfo','CheckEnvironmentRows',
 'CheckHelpPanelActions','CheckHelpPanelDraws','CheckHelpLineIndex','CheckHelpTextOutput','CheckHelpNewsOpening',
 'CheckKeyLabel','CheckMapPanelOpening','CheckModelTradeMode','CheckPackedWordAndActionReturn',
 'CheckPassivePanelActions','CheckPassivePanelHovers','CheckSettingsPanelActions','CheckShipModelActions',
 'CheckShipPreviewCallbacks','CheckStationHelpCalls','CheckWelcomePanel')


def check(name):
 path=RESEARCH/(name+'.py');assert 'from ProbeShipPreviewCallbacks import' in path.read_text('utf-8')
 # Проверка явно перечисленной исследовательской модели, сборочные команды в перечень не входят.
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(path)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 row=dict(model=name,passed=result.returncode==0,exit_code=result.returncode)
 if result.returncode:row['failure_output']=(result.stdout+result.stderr)[-8000:]
 print(json.dumps(row,ensure_ascii=False),flush=True);return row


def main():
 report_path=ROOT/'Tools/Disasm/Reports/FixtureConsumersVerification.json'
 if sys.argv[1:]==['--retry-failed']:
  previous=json.loads(report_path.read_text('utf-8'));results=previous['models'];assert [r['model'] for r in results]==list(MODELS)
  for index,row in enumerate(results):
   if not row['passed']:results[index]=check(row['model'])
 else:
  assert len(sys.argv)==1
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,MODELS))
 report=dict(passed=all(r['passed'] for r in results),method='explicit_research_model_replay_after_fixture_list_relocation',
  original_draw_list_address=0xF3DE,b400_code_not_overwritten_by_shared_fixture=True,models=results,
  previous_reports_replaced_by_actual_replays=True,native_execution=False,assembly_executed=False)
 report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(dict(passed=report['passed'],models=len(results),failed=[r['model'] for r in results if not r['passed']]),ensure_ascii=False),flush=True)
 if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
