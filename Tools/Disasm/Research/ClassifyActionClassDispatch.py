"""Защищённая публикация доказанного косвенного диспетчера."""
import ActionClassDispatchFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionClassDispatch','ActionClassDispatch',state_fields=(
        ('ClassTable',0x64F0,'существующие 26 адресов, индекс вне таблицы исходный код не ограничивает'),))
