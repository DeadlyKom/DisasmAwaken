"""Точечная публикация интервальной проверки без изменения исходных инструкций."""
import ActionFoldedNearWordsFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionFoldedNearWords','ActionFoldedNearWords',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionNearWordsConst',facts.BLOCK),))
