"""Публикация проверенного выбора кода 26 либо фильтрованного индекса."""
import ActionRandomFilteredRecordFacts as facts
from PublishActionRawFunction import main

if __name__=='__main__':
    main(facts,'ActionRandomFilteredRecord',0xE6E2,0xE70D,81745,allow_subrange=True)
