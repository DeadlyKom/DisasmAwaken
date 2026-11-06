"""Публикация полностью перебранного трёхбайтового максимума."""
import ActionVectorHighMaximumFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionVectorHighMaximum','ActionVectorHighMaximum',state_fields=(
        ('High0',0x9B71,'старший байт первой трёхбайтовой рабочей компоненты'),
        ('High1',0x9B74,'старший байт второй трёхбайтовой рабочей компоненты'),
        ('High2',0x9B77,'старший байт третьей трёхбайтовой рабочей компоненты')))
