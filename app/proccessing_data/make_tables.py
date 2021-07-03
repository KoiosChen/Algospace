from app.models import TransferOrders

result_dict = {0: "拒绝", 1: "通过"}


def make_table_transfer_orders(lines=None):
    if lines is None:
        lines = TransferOrders.query.all()
    result = [{"DT_RowId": "row_" + str(l.id),
               "id": l.id,
               "filename": l.filename,
               "apply_reason": l.apply_reason if l.apply_reason else "",
               "apply_type": l.apply_type.name if l.apply_type_id else "",
               "apply_at": l.apply_at,
               "share_to": '<br>'.join(u.username for u in l.sendto),
               "confirm_user": l.confirm_user.username if l.confirm_user_id else "",
               "confirm_result": result_dict.get(l.confirm_result),
               "confirm_at": l.confirm_at if l.confirm_at else "",
               } for l in lines]
    print(result)
    return result


def make_table_confirm_transfer_orders(lines=None):
    if lines is None:
        lines = TransferOrders.query.all()
    result = [{"DT_RowId": "row_" + str(l.id),
               "id": l.id,
               "filename": l.filename,
               "apply_user": l.apply_user.username if l.apply_user_id else "",
               "apply_reason": l.apply_reason if l.apply_reason else "",
               "apply_type": l.apply_type.name if l.apply_type_id else "",
               "apply_at": l.apply_at,
               "share_to": '<br>'.join(u.username for u in l.sendto),
               "confirm_result": result_dict.get(l.confirm_result),
               "confirm_user": l.confirm_user.username if l.confirm_user_id else "",
               "confirm_at": l.confirm_at if l.confirm_at else "",
               } for l in lines]
    print(result)
    return result
