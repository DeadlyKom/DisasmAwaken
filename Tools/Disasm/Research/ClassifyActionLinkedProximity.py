"""Публикация 52 исходных байтов State0E с явно ограниченной моделью большого пути."""
from PublishActionRawFunction import main
import ActionLinkedProximityFacts as facts

if __name__=='__main__':main(facts,'ActionLinkedProximity',0xF009,0xF03D,106496,allow_subrange=True)
