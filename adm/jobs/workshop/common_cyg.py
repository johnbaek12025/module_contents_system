from adm.jobs import (
    get_kor_name,
    get_dealing_str,
    get_size_str,
    get_size_symbol,
    get_size_color,
    get_unit_str,
    get_size_style,
    get_value_style,
)


def get_bottom_values(
    db_mgr,
    analysis_type,
    deal_date,
    dealing_type,
    subject,
    stock_code,
    unit,
    accumulated_days=1,
):
    value_dict = db_mgr.get_7254_accu_value(
        deal_date,
        stock_code,
        "sonmeme",
        unit,
        accumulated_days,
    )
    master_info = db_mgr.get_master_info(deal_date, stock_code)

    return_dict = dict()
    for s in subject:
        value = value_dict[s]
        return_dict[s] = {
            "sub": get_kor_name(s),
            "dt": get_dealing_str(value),
            "abs_val": format(abs(value), ","),
            "val": format(abs(value), ","),
            "ratio": round(abs(value) / master_info["total_stock"] * 100, 2),
            "size": get_size_str(dealing_type),
            "unit": get_unit_str(unit),
            "size_style": get_size_style(value),
        }
    return return_dict


def get_bottom_values_sum(
    db_mgr,
    analysis_type,
    deal_date,
    dealing_type,
    subject,
    stock_code,
    unit,
    accumulated_days,
):
    """
    def get_bottom_values 함수에  accumulated_days=1로 fix되어 있어서 함수를 추가함
    """
    value_dict = db_mgr.get_7254_accu_value_sum(
        deal_date,
        stock_code,
        "sonmeme",
        unit,
        accumulated_days,
    )
    master_info = db_mgr.get_master_info(deal_date, stock_code)

    return_dict = dict()
    for s in subject:
        value = value_dict[s]
        return_dict[s] = {
            "sub": get_kor_name(s),
            "dt": get_dealing_str(value),
            "abs_val": format(abs(value), ","),
            "val": format(value, ","),
            "ratio": round(abs(value) / master_info["total_stock"] * 100, 2),
            "size": get_size_str(dealing_type),
            "unit": get_unit_str(unit),
            "value_style": get_value_style(value),
        }
    return return_dict


def get_stock_list_str(stock_list):
    if len(stock_list):
        stock_list_str = f"{', '.join(stock_list)} 등"
    else:
        stock_list_str = "없음"
    return stock_list_str