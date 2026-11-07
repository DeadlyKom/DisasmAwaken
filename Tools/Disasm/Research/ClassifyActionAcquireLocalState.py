"""Публикация исходных 16 байтов State12 с физическим продолжением в существующем хвосте."""
from PublishActionRawFunction import main
import ActionAcquireLocalStateFacts as facts

if __name__=='__main__':main(facts,'ActionAcquireLocalState',0xF6BD,0xF6CD,73984,allow_subrange=True)
