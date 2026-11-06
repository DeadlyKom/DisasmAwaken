"""Выделение доказанного алгоритма Class09 из физического диапазона обработчиков."""
import ActionClass9LinkFacts as facts
from PublishActionRawFunction import main

if __name__=='__main__':
    main(facts,'ActionClass9Link',0x65C6,0x65DE,72192,allow_subrange=True)
