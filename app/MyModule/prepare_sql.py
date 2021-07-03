from app import logger
from .process_datetime import format_daterange
from app.models import TransferOrders, Users, ApplyTypes
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from sqlalchemy import or_, and_


def search_sql(post_data, advance=None):
    """

    :param post_data: it's request.form object from post data
    :param tab: it's a list
    :return: count, search result
    """
    logger.info(f"Query transfer orders by {post_data}")

    page_start = int(post_data.get('start'))
    length = int(post_data.get("length"))
    search_field = eval(post_data.get('search_field')) if 'search_field' in post_data.keys() else []
    search_content = post_data.get('search_content') if post_data.get('search_content') else ""
    search_field_date = post_data.get('search_field_date') if post_data.get('search_field_date') else 'apply_at'
    search_date_range = post_data.get('search_date_range')

    concat_fields = list()
    or_fields_list = list()

    start_time, stop_time = format_daterange(search_date_range)

    original_search_field = search_field

    apply_users = aliased(Users)
    confirm_users = aliased(Users)
    apply_types = aliased(ApplyTypes)

    if len(search_field) == 0:
        search_field = ["filename", "apply_user", "confirm_result", "confirm_user"]

    base_sql = TransferOrders.query

    if search_content:
        for f in search_field:
            if f == 'filename':
                concat_fields.append(func.ifnull(TransferOrders.filename, ''))
            elif f == 'apply_user':
                base_sql = base_sql.outerjoin(apply_users, apply_users.id == TransferOrders.apply_user_id)
                or_fields_list.append(apply_users.username.contains(search_content))
            elif f == 'confirm_result':
                if search_content in "通过":
                    or_fields_list.append(TransferOrders.confirm_result.__eq__(1))
                elif search_content in "拒绝":
                    or_fields_list.append(TransferOrders.confirm_result.__eq__(0))
            elif f == 'confirm_user':
                base_sql = base_sql.outerjoin(confirm_users, confirm_users.id == TransferOrders.confirm_user_id)
                or_fields_list.append(confirm_users.username.contains(search_content))
            elif f == 'apply_type':
                base_sql = base_sql.outerjoin(apply_types, apply_types.id == TransferOrders.apply_type_id)
                or_fields_list.append(apply_types.name.contains(search_content))

    if advance is None:
        fuzzy_sql = or_(func.concat(*concat_fields).contains(search_content),
                        *or_fields_list) if concat_fields else or_(*or_fields_list)
    else:
        fuzzy_sql = and_(advance, or_(func.concat(*concat_fields).contains(search_content),
                                      *or_fields_list) if concat_fields else or_(*or_fields_list))

    logger.debug(search_field_date)

    daterange_sql = and_(getattr(TransferOrders, search_field_date).__le__(stop_time),
                         getattr(TransferOrders, search_field_date).__ge__(start_time))
    if post_data.get('search_field_date'):
        final_sql = base_sql.filter(fuzzy_sql, daterange_sql)
    else:
        final_sql = base_sql.filter(fuzzy_sql)

    logger.debug(final_sql)

    records_total = final_sql.group_by(TransferOrders.id).count()

    logger.debug(f">>>> Lines: {records_total} Pages: {int(records_total / length)} from {page_start} to {length}")

    return records_total, final_sql.order_by(TransferOrders.apply_at.desc()).offset(
        page_start).limit(length).all()
