"""Публикация полного табличного кодировщика знакового отношения."""
import ActionSignedRatioCodeFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionSignedRatioCode','ActionSignedRatioCode',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionRatioCodeConst',facts.BLOCK),))
