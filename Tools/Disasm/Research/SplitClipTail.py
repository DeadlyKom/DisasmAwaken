"""Однократное выделение двенадцати проверенных помощников из общего хвоста отсечения."""
from SplitClipProducts import main


if __name__=='__main__':
 starts=(0xDAB0,0xDABB,0xDAC6,0xDAD1,0xDADC,0xDAF0,0xDB04,0xDB18,0xDB2C,0xDB37,0xDB42,0xDB59,0xDB63)
 main(dict(history='BeforeClipTailSplit',candidate='ClipTailScoped',model='ClipTailVerification',address=0xDAB0,end=0xDB63,
  parts=tuple((begin,end,'Unknown'+format(begin,'04X')) for begin,end in zip(starts,starts[1:]))))
