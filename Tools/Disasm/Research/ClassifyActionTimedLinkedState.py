"""Публикация исходных 40 байтов State10 с реальными общими продолжениями."""
from PublishActionRawFunction import main
import ActionTimedLinkedStateFacts as facts

if __name__=='__main__':main(facts,'ActionTimedLinkedState',0xF3C8,0xF3F0,65536,allow_subrange=True)
