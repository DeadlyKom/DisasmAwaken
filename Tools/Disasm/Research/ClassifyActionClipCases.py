"""Публикация доказанных Case-входов через отдельного кандидата, без массового экспорта."""
from ClassifyActionRegionType import main
import ActionClipCasesFacts as facts

if __name__=="__main__":main(facts,"ActionClipCases","ActionClipCases",(("SeenFlags",0xCF07,"отметки TL, TR, BL, BR в битах 3..0, старшая тетрада сохраняется"),),allow_named=True)
