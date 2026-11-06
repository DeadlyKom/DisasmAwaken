"""Публикация доказанного продолжения EA3D..EAE8."""
import ActionLargeEffectContinuationFacts as facts
from PublishActionRawFunction import main


if __name__ == '__main__':
    main(facts, 'ActionLargeEffectContinuation', 0xEA3D, 0xEAE9, 640, allow_subrange=True,
         proof_tag='ActionLargeEffectChildren')
