"""Однократное применение доказанных масок к внутренним хвостам Unknown-ядра."""
from AnnotateClipCases import main
from ArcClosingFacts import COMMENTS,LABELS,name_operands


if __name__=='__main__':
 main(dict(history='BeforeArcClosingNotes',candidate='ArcClosingScoped',addresses=(0xE2AB,),comments=COMMENTS,labels=LABELS,
  operands=name_operands,document='ArcClosing',title='битовые маски завершения и сохранённый стековый кадр'))
