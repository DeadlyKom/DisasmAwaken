"""Точечный выпуск подготовителя и двух направлений внутренней заливки."""
import ControlsInteriorRowsFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts,'ControlsInteriorRows','ControlsInteriorRows',(
        ('Mode',0xD18C,'общий байт режима, его нулевое состояние возвращается в Z'),
        ('RowStep',0xD5B5,'операнд LD DE, nn, шаг строки -32 либо 32'),
        ('BoundaryLimit',0xD600,'операнд CP, верхняя либо нижняя граница страницы'),
        ('BoundaryBranch',0xD601,'сам код JR C либо JR NC после проверки границы')))
