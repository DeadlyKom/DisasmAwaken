"""Однократный перенос проверенной подготовки геометрии в два сохраняющих Unknown фрагмента."""
from AnnotateClipCases import main
from ArcGeometryFacts import COMMENTS,LABELS,name_operands


if __name__=='__main__':
 main(dict(history='BeforeArcGeometryNotes',candidate='ArcGeometryScoped',addresses=(0xC000,0xDFC3),
  comments=COMMENTS,labels=LABELS,operands=name_operands,document='ArcWorkspace',
  title='физические поля, знаки квадранта и проверенная подготовка геометрии'))
