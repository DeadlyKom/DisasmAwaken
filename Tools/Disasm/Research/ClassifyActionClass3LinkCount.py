"""Публикация насыщенного счётчика и адресных смыслов одинаковых литералов."""
import ActionClass3LinkCountFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionClass3LinkCount','ActionClass3LinkCount',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionClass3CountConst',facts.BLOCK),))
