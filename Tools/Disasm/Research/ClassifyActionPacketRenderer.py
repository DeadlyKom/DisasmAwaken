"""Выделение полного DD23 с сохранением родителя DBBD и его прежних банковых писателей."""
from PublishActionRawFunction import main
import ActionPacketRendererFacts as facts

if __name__=='__main__':main(facts,'ActionPacketRenderer',0xDD23,0xDDD1,1850,allow_subrange=True)
