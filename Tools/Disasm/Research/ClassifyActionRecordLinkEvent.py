"""Публикация локального преобразования записи, неизвестный производитель указателя не скрывается."""
from ClassifyActionRegionType import main
import ActionRecordLinkEventFacts as facts


if __name__=='__main__':
    main(facts,'ActionRecordLinkEvent','ActionRecordLinkEvent',(
        ('PendingRecord',0x635C,'операнд LD HL,nn по 635B, ноль либо база записи, производитель ещё неизвестен'),))
