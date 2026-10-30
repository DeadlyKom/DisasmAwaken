"""Однократное выделение исходного 24-байтового состояния из сохранённого физического диапазона."""
from ClassifyMapLineTables import main
from ArcWorkspaceTable import DATA,render


if __name__=='__main__':
 main(dict(history='BeforeArcWorkspace',candidate='ArcWorkspaceScoped',model='ArcGeometryPrefixVerification',render=render,
  parts=(('AfterClipProducts.bin',((0x1E7B,0x1FAB,'unclassified','Source/Resources/07_KARTA/BeforeArcWorkspace.bin'),
   (0x1FAB,0x1FC3,'typed_data',DATA))),)))
