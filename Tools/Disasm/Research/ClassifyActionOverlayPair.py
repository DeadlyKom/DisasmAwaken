"""Публикация исходных 45 байтов EB41 с полным разбором дочернего вывода."""
from PublishActionRawFunction import main
import ActionOverlayPairFacts as facts

if __name__=='__main__':main(facts,'ActionOverlayPair',0xEB41,0xEB6E,4825,allow_subrange=True)
