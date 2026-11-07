"""Два доказанных входа, три соседних байта отдельного перехода сохраняются отдельно."""
from PublishActionRawFunction import main
import ActionIdleBaseResetFacts as reset
import ActionIdleStateFacts as state

if __name__=='__main__':
    main(reset,'ActionIdleBaseReset',0xF691,0xF69E,196608,allow_subrange=True,proof_tag='ActionIdleState')
    main(state,'ActionIdleState',0xF67F,0xF68E,196608,allow_subrange=True)
