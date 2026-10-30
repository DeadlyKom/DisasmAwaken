"""Однократное оформление 51 исходного байта станции без отдельного добавленного ограничителя."""
from ClassifyMapLineTables import main
from AuxiliaryMapTables import KEYS,CODES,render


if __name__=='__main__':
 main(dict(history='BeforeAuxiliaryMapTables',candidate='AuxiliaryMapTablesScoped',model='MapSceneVerification',render=render,
  slot=4,origin=0x6000,resource_dir='04_STATIONF',
  parts=(('AfterStoredMapOrder.bin',((0x397B,0x39A3,'typed_data',KEYS),(0x39A3,0x39AE,'typed_data',CODES))),)))
