"""Публикация девяти исходных байтов и доказанного контракта без выделения памяти."""
from PublishActionRawFunction import main
import ActionRecordSelectionFacts as facts

if __name__=='__main__':main(facts,'ActionRecordSelection',0xE69E,0xE6A7,65536)
