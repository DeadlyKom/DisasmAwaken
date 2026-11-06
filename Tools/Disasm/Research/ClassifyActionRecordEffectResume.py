"""Публикация двух инструкций F7BF..F7C5."""
import ActionRecordEffectResumeFacts as facts
from PublishActionRawFunction import main


if __name__ == '__main__':
    main(facts, 'ActionRecordEffectResume', 0xF7BF, 0xF7C6, 4096,
         proof_tag='ActionRecordEffectThreshold')
