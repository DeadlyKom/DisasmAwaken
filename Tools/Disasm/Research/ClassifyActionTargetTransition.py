"""Выделение исходных 23 байтов без создания новой команды хвостового перехода."""
from PublishActionRawFunction import main
import ActionTargetTransitionFacts as facts

if __name__=='__main__':main(facts,'ActionTargetTransition',0xE91E,0xE935,67072,allow_subrange=True)
