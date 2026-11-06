"""Публикация точного локального договора приближённого отношения, без сборки."""
from ClassifyActionRegionType import main
import ActionLogRatioFacts as facts


if __name__=='__main__':
    main(facts,'ActionLogRatio','ActionLogRatio',(
        ('ShiftFraction',0xAF14,'изменяемое смещение JR NZ по AF13, обычные значения 0..7'),
        ('ShiftInteger',0xAF2F,'изменяемое смещение JR NZ по AF2E, обычные значения 0..7')))
