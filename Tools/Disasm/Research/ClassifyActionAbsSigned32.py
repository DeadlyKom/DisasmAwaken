"""Точечная публикация полного 32-битного модуля."""
import ActionAbsSigned32Facts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionAbsSigned32','ActionAbsSigned32',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionAbs32Const',facts.BLOCK),))
