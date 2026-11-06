"""Побайтовая пометка записи по IY, протокол совпадает с исследованным setter по IX."""
from ActionRecordReuseFacts import CONTRACTS as IX_CONTRACTS,COMMENTS as IX_COMMENTS
FUNCTIONS={0xF03D:('MarkIYRecordForReuse','Пометка записи по IY кодом Component0=8000 и однократным пропуском ReuseByte=FF')}
LOCAL={}
CONTRACTS={('Action',0xF03D):tuple([
    line.replace('IX - адрес','IY - адрес').replace('F394..F3A0','F03D..F049')
        .replace('настоящий MarkRecordForReuse','настоящий MarkIYRecordForReuse') for line in section]
    for section in IX_CONTRACTS['Action',0xF394])}
COMMENTS={address-0xF394+0xF03D:value for address,value in IX_COMMENTS.items()}


def name_operands(region,address,operation):
    if region!='Action':return operation
    if operation.startswith(('CALL ','JP ')):
        operation=operation.replace('#F03D','@Action.MarkIYRecordForReuse.Entry')
    if address!=0xF03D:return operation
    for before,after in (('(IY+#01)','(IY+FActionRecord.Components.Component0.High)'),
        ('(IY+#00)','(IY+FActionRecord.Components.Component0.Low)'),('(IY+#18)','(IY+FActionRecord.ReuseByte)'),
        (', #80',', @ActionReuseConst.ReusableHigh'),(', #00',', @ActionReuseConst.ReusableLow'),(', #FF',', @ActionReuseConst.SkipOnce')):
        operation=operation.replace(before,after)
    return operation
