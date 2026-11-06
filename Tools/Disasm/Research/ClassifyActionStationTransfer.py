"""Публикация короткого банкового хвоста 6CE4, цель DCE3 не выдаётся за исполненную."""
from PublishActionRawFunction import main
import ActionStationTransferFacts as facts


if __name__=='__main__':main(facts,'ActionStationTransfer',0x6CE4,0x6CEF,16384)
