"""Два физических входа с сохранением отдельных 16 байтов пока не доказанного State12."""
from PublishActionRawFunction import main
import ActionLocalOffsetsFacts as core
import ActionFastPhaseStateFacts as state

if __name__=='__main__':
    main(core,'ActionLocalOffsets',0xF6CD,0xF6EC,131072,allow_subrange=True,proof_tag='ActionLocalOffsetState')
    main(state,'ActionFastPhaseState',0xF6AB,0xF6BD,131072,allow_subrange=True,proof_tag='ActionLocalOffsetState')
