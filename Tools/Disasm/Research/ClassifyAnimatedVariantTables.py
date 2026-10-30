"""Точечное оформление 894 исходных байтов данных потребителя C677."""
from ClassifyMapLineTables import main
from AnimatedVariantTables import RANGES,render


if __name__=='__main__':
 main(dict(history='BeforeAnimatedVariantTables',candidate='AnimatedVariantTablesScoped',model='AnimatedVariantTablesVerification',render=render,
  parts=(('BeforeMarkerSprites.bin',tuple((begin,end,'typed_data',path) for begin,end,path in RANGES)),)))
