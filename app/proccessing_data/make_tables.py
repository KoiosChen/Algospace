from app.models import TransferOrders, FILE_URL, ConfigFiles, ConfigKeys, ConfigValues, result_dict
import json
from app.proccessing_data.public_methods import get_table_data, get_table_data_by_id
from collections import defaultdict




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
               "filename": f"<a href='{FILE_URL}/{l.file_store_path}' download='{l.filename}'>{l.filename}</a>",
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


def make_table_config_files(config_file_id, key_id=None, raw=None):
    if not key_id:
        advance_search = [{"key": "config_file_id", "value": config_file_id, "operator": "__eq__"},
                          {"key": "parent_id", "value": None, "operator": "__eq__"}]
        all_keys = get_table_data(ConfigKeys, {}, appends=['children', 'my_values'], advance_search=advance_search)
    else:
        advance_search = [{"key": "config_file_id", "value": config_file_id, "operator": "__eq__"},
                          {"key": "id", "value": key_id, "operator": "__eq__"},
                          {"key": "parent_id", "value": None, "operator": "__eq__"}]
        all_keys = get_table_data(ConfigKeys, {}, appends=['children', 'my_values'], advance_search=advance_search)

    result = list()

    def find_child(key_children):
        list_record = defaultdict(dict)
        for kc in key_children:
            if kc.get('children'):
                list_record[kc['order']][kc['name']] = find_child(kc.get('children'))
            else:
                list_record[kc['order']][kc['name']] = kc['my_values']
        if len(list_record.keys()) == 1:
            return_data = list_record.pop(0)
        else:
            return_data = list()
            for k, v in list_record.items():
                return_data.append(v)
        return return_data

    for k in all_keys['records']:
        if k.get('children'):
            x = find_child(k.get('children'))
            result.append({"DT_RowId": "row_" + "1",
                           "id": k["id"],
                           "key": k["name"],
                           "value": json.dumps(x) if raw is None else x,
                           "version": k["version"],
                           "status": k["status"], })
        else:
            result.append({"DT_RowId": "row_" + "1",
                           "id": k["id"],
                           "key": k["name"],
                           "value": json.dumps(k["my_values"]) if raw is None else k["my_values"],
                           "version": k["version"],
                           "status": k["status"], })
    return result
