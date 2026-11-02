"""Публикация двух самостоятельных входов после проверки реальных страниц памяти."""
import ActionParameterActivationFacts as facts
from ClassifyActionRegionType import main


if __name__=='__main__':
    main(facts,'ActionParameterActivation','ActionParameterActivation',(
        ('UnknownWord0',0xECA9,'первое обнуляемое слово банка 0, игровой смысл не установлен'),
        ('UnknownWord1',0xECF6,'второе обнуляемое слово банка 0, игровой смысл не установлен'),
        ('UnknownByte0',0x9B83,'первый обнуляемый байт фиксированного банка 2, игровой смысл не установлен'),
        ('UnknownByte1',0x9B82,'второй обнуляемый байт фиксированного банка 2, игровой смысл не установлен'),
    ))
