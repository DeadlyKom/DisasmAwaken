"""Все значения сохранённого CPU-SP, одно настоящее LD SP без исполнения следующей очереди."""
import json
from ProbePreviewPolygon import context,ROOT
from skoolkit.simutils import PC


def main():
 m,s,initial=context()
 for value in range(65536):
  m.recording=False;m[0xEEEF:0xEEF1]=[value&255,value>>8];s.registers[:]=initial;r=s.registers;r[PC]=0xEEEE;m.recording=True;m.writes=[]
  # Проверка восстановления произвольного слова SP без чтения старого стека и изменения остальных регистров.
  s.run();assert r[PC]==0xEEF1 and r[12]==value and r[:12]==initial[:12] and r[16:24]==initial[16:24] and not m.writes
 report=dict(passed=True,cases=65536,all_saved_sp_words=True,all_main_alternate_index_context_preserved=True,no_memory_writes=True,real_ld_sp_executed=True,
  next_queue_not_executed=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewStackRestoreVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
