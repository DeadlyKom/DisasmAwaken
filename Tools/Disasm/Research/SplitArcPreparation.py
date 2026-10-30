"""Однократное разделение двух доказанных подготовок и следующих за ними растровых входов."""
from SplitClipProducts import main


if __name__=='__main__':
 for begin,middle,end,tag in ((0xE208,0xE228,0xE248,'FullSpan'),(0xE299,0xE2AB,0xE514,'ClippedInputs')):
  main(dict(history='BeforeArc'+tag+'Split',candidate='Arc'+tag+'Scoped',model='ArcPreparationVerification',address=begin,end=end,
   document='ArcPreparation',description='Unknown, самостоятельный фрагмент подготовки и растрового обхода дуги',
   parts=((begin,middle,'Unknown'+format(begin,'04X')),(middle,end,'Unknown'+format(middle,'04X')))))
