"""Публикация 235 исходных байтов State08 с полным внешним возвратом."""
from PublishActionRawFunction import main
import ActionArrivalStateFacts as facts

if __name__=='__main__':main(facts,'ActionArrivalState',0xF57F,0xF66A,70256,allow_subrange=True)
