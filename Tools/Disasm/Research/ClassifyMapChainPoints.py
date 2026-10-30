"""Однократное оформление текущей и предыдущей точек без изменения разнесённой таблицы."""
from ClassifyMapLineTables import main
from MapChainPointTables import render,CURRENT,PREVIOUS


if __name__=='__main__':
 main(dict(history='BeforeMapChainPointTables',candidate='MapChainPointTablesScoped',model='MapPointChainVerification',render=render,
  parts=(('BeforeMapLinePoints.bin',(
   (0x1DB0,0x1E0B,'unclassified','Source/Resources/07_KARTA/BeforeMapChainPoints.bin'),
   (0x1E0B,0x1E10,'typed_data',CURRENT),
   (0x1E10,0x1E1B,'unclassified','Source/Resources/07_KARTA/BetweenMapChainPoints.bin'),
   (0x1E1B,0x1E20,'typed_data',PREVIOUS),
   (0x1E20,0x1E2B,'unclassified','Source/Resources/07_KARTA/AfterMapChainPoints.bin'))),)))
