"""Публикация 41 исходного байта координатной обёртки без изменения геометрии."""
from PublishActionRawFunction import main
import ActionSelectedRecordStepFacts as facts

if __name__=='__main__':
    main(facts,'ActionSelectedRecordStep',0xF36B,0xF394,393728,allow_subrange=True)
