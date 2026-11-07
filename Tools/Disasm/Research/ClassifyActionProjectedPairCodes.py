"""Публикация исходных 84 байтов EC54 без изменения памяти и алгоритма."""
from PublishActionRawFunction import main
import ActionProjectedPairCodesFacts as facts

if __name__=='__main__':main(facts,'ActionProjectedPairCodes',0xEC54,0xECA8,268705,allow_subrange=True)
