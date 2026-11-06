"""Разделение хвоста 7DD4 с сохранением последовательного исполнения."""
from SplitActionWorkVectorEntry import main


if __name__ == '__main__':
    main(0x7B58, 0x7DD4, tag='ActionSpawnRecordFinishSplit',
         proof_name='ActionSpawnRecordFinishVerification',
         proof_fields=('whole_object_record_compared', 'stops_before_class_dispatch'),
         previous_instruction='CALL @Action.StepRecordTowardWideVector.Entry', continuation=True)
