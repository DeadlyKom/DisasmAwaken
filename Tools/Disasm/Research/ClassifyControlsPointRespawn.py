"""Публикация двух функций после извлечения исходного динамического входа CE5D."""
import json
import ControlsPointRespawnFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__=='__main__':
    assert json.loads((ROOT / 'Tools/Disasm/Reports/ControlsPointRespawnDispatchVerification.json').read_text('utf-8'))['passed']
    main(facts,'ControlsPointRespawn','ControlsPointRespawn',(
        ('PositivePhase',0xCE17,'фазовый байт входа при неотрицательном индексе'),
        ('PositiveStep',0xCE1E,'ненулевой шаг входа при неотрицательном индексе'),
        ('PositiveYOffset',0xCE31,'смещение Y первой ветви этого входа'),
        ('NegativePhase',0xCE5E,'фазовый байт входа при отрицательном индексе'),
        ('NegativeStep',0xCE65,'ненулевой шаг входа при отрицательном индексе'),
        ('NegativeYOffset',0xCE78,'смещение Y первой ветви этого входа')))
