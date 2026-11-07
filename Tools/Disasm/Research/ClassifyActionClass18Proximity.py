"""Публикация 21 исходного байтов подтверждённой цели состояния 0C."""
from PublishActionRawFunction import main
import ActionClass18ProximityFacts as facts

if __name__=='__main__':
    main(facts,'ActionClass18Proximity',0xF356,0xF36B,958,allow_subrange=True)
