"""Однократное представление шести исходных ресурсов структурированными фазами без изменения байтов."""
from ClassifyMapLineTables import main
from MarkerSpriteTables import RANGES,render


if __name__=='__main__':
 parts=[(0x0A45,0x0DC3,'unclassified','Source/Resources/07_KARTA/BeforeMarkerSprites.bin')]
 parts.extend((begin-0xC000,end-0xC000,'typed_data',path) for begin,end,path in RANGES)
 main(dict(history='BeforeMarkerSprites',candidate='MarkerSpritesScoped',model='MarkerSpriteResourcesVerification',render=render,
  parts=(('EventGap0A45.bin',tuple(parts)),)))
