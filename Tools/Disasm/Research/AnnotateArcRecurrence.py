"""Однократное внесение проверенной двухкраевой рекурсии, остальные входы остаются Unknown."""
from AnnotateClipCases import main
from ArcRecurrenceFacts import COMMENTS,LABELS,name_operands


if __name__=='__main__':
 main(dict(history='BeforeArcRecurrenceNotes',candidate='ArcRecurrenceScoped',addresses=(0xE2AB,0xE69D,0xE6A4),
  comments=COMMENTS,labels=LABELS,operands=name_operands,document='ArcRecurrence',
  title='проверенная двухкраевая рекурсия и границы её модели'))
