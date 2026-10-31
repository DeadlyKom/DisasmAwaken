"""Документирование проверенного реестра путей D3D, исходники не перезаписываются."""
from pathlib import Path
import json
from DescribeClipDecisions import ZONE,describe_action,describe_condition
ROOT=Path(__file__).resolve().parents[3]


def main():
 report=json.loads((ROOT/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').read_text('utf-8'))
 assert json.loads((ROOT/'Tools/Disasm/Reports/PreviewClipCaseSemanticsVerification.json').read_text('utf-8'))['passed']
 lines=['# Все табличные пути отсечения D3D','',
  '[Обработчики](../Source/D3D/PreviewClipCases.asm) и [контракт группы](PreviewClipCases.md).',
  '', 'I означает внутреннюю точку, R/L/B/T внешние стороны. Составные имена обозначают угловые зоны. Реестр раскрывает фактический граф, независимое доказательство геометрии не заявляется.',
  '', 'Разность произведений обёрнута до 32 бит, разность координат до 16 бит. X2−X1 в исходном реестре означает разность колонок, Y2−Y1 разность строк. Равенство входит в неотрицательную ветвь. Умножение и проекция имеют особенности из [произведений](PreviewClipProducts.md) и [пересечений](PreviewClipIntersections.md).',
  '', 'Запрос угла пишет точку только при BlockCode=0. Отметка изменяется независимо от BlockCode. Проверка прежней отметки учитывает предыдущие SET этого пути. Обычный и специальный выходы используют кадр внешнего диспетчера.', '']
 for case in report['cases']:
  lines+=['## '+ZONE[case['first']]+' → '+ZONE[case['second']]+' ('+format(case['entry'],'04X')+')','']
  for path in case['paths']:
   condition=' и '.join(describe_condition(c) for c in path['conditions']) or 'без дополнительных условий'
   actions=', затем '.join(describe_action(a) for a in path['actions']) or 'выходные точки и отметки не добавляются'
   lines+=['- '+condition+' — '+actions+', '+('специальный выход' if path['exit']=='special' else 'обычный выход')+'.']
  lines+=['']
 (ROOT/'Docs/PreviewClipCaseDecisions.md').write_text('\n'.join(lines),'utf-8')
 print('Documented',len(report['cases']),'physical pairs and',sum(len(c['paths']) for c in report['cases']),'paths')


if __name__=='__main__':main()
