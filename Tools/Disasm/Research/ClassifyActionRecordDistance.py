"""Выделение 88 байтов вычислителя, следующий проекционный участок сохраняется отдельно."""
from PublishActionRawFunction import main
import ActionRecordDistanceFacts as facts

if __name__=='__main__':
    main(facts,'ActionRecordDistance',0xEAE9,0xEB41,197337,allow_subrange=True)
