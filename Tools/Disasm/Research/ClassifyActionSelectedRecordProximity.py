"""Публикация 43 исходных байтов подтверждённой цели состояния 0D."""
from PublishActionRawFunction import main
import ActionSelectedRecordProximityFacts as facts

if __name__=='__main__':
    main(facts,'ActionSelectedRecordProximity',0xF04A,0xF075,1024)
