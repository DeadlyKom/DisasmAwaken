"""Последовательная защищённая публикация трёх проверенных фильтров без массового экспорта."""
from importlib import import_module
from PublishActionRawFunction import main

if __name__=='__main__':
    for tag,start in (('ActionRecordsExcept6And7',0xE70D),('ActionRecords6Or7',0xE729),('ActionRecords5Or14',0xE745)):
        main(import_module(tag+'Facts'),tag,start,start+28,14929,allow_subrange=True)
