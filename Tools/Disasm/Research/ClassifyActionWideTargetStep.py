"""Точечная публикация писателя и подготовки координат без переноса памяти."""
import ActionWideTargetStepFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionWideTargetStep','ActionWideTargetStep',state_fields=(),include_blocks=(
        ('Includes/Structs/Include.inc','struct FActionWideComponent',facts.STRUCT_BLOCK),))
