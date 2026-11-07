"""Публикация 21 исходного байта цели состояния 07."""
from PublishActionRawFunction import main
import ActionTimedDecayStateFacts as facts

if __name__=='__main__':main(facts,'ActionTimedDecayState',0xF66A,0xF67F,131072,allow_subrange=True)
