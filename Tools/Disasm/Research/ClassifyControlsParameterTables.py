"""Публикация полного DE10, исходные размещения и наложение шаблона сохранены."""
import ControlsParameterTablesFacts as facts
from ClassifyControlsTextDisplay import main


if __name__=='__main__':
    main(facts,'ControlsParameterTables','ControlsParameterTables',(
        ('SeedFirst',0x9BC1,'первое слово зерна из существующего контекста'),
        ('SeedSecond',0x9BC3,'второе слово зерна из существующего контекста'),
        ('StepControl',0x9BC5,'управляющий байт числа шагов генератора'),
        ('SeedIndex',0x688B,'изменяемый операнд LD A, n по 688A общего ядра ACTION'),
        ('Parameters',0x9BA4,'пятнадцать последовательных вычисляемых байтов'),
        ('CoordRows',0x7B97,'первая из девяти записей с физическим шагом шесть'),
    ))
