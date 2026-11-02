"""Публикация четырёх проверенных подготовителей без изменения размещения."""
import ControlsCircleSetupFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsCircleSetup', 'ControlsCircleSetup', (
        ('WorkY', 0xD181, 'младший байт исходной рабочей пары Y и X'),
        ('WorkX', 0xD182, 'старший байт исходной рабочей пары Y и X'),
        ('CenterY', 0xD183, 'байтовая строка центра в подготовителях края'),
        ('SectionRadius', 0xD185, 'байт сечения, загружаемый в альтернативный E'),
    ))
