"""Публикация 234 исходных байтов State02, включая четыре доказанных дополнительных входа."""
from PublishActionRawFunction import main
import ActionLinkedTargetStateFacts as facts

if __name__=='__main__':main(facts,'ActionLinkedTargetState',0xF138,0xF222,44656,allow_subrange=True)
