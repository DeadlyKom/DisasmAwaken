"""Применение составного договора цикла без смены адресов или имён."""
from MainLoopControlFacts import FUNCTIONS, DOCUMENTS, LABELS, CONTRACTS, COMMENTS, name_operands as control_name_operands
RENAMES={}
IN_PLACE={0x9A59}

import re
TARGETS={43433: 'MarketState.MarkMode', 43291: 'Station.GenerateMarket.Entry', 40055: 'Station.RebuildInterface.Entry', 25494: 'Station.SelectRamBank.Entry', 38970: 'ScriptCallState.EventCode', 39512: 'Station.EmptyCallback.Entry', 39568: 'InterfaceState.HoverCallback', 39606: 'Station.MainLoop.CheckTransition', 39554: 'InterfaceState.EventEnabled', 39618: 'Station.MainLoop.PollActions', 32346: 'Station.HandleItem08.BeginTransition', 41983: 'Station.SaveTextWindow.Entry', 42734: 'Station.DrawItem01.Entry', 42038: 'Station.RestoreTextWindow.Entry', 40003: 'Station.MergeActionInputs.Entry', 39553: 'Station.MainLoop.Frame', 39652: 'Station.MainLoop.DispatchAction', 40567: 'Station.CloseActiveItem.Entry', 40378: 'Station.DispatchInterfaceEvent.Entry'}

def name_operands(region,address,operation):
 operation=control_name_operands(region,address,operation)
 if region=="Station" and address==0x9A59:
  operation=re.sub(r"#([0-9A-F]{4})",lambda m:"@"+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation
