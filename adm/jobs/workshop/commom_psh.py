import datetime
from adm.jobs import get_time_period, get_previous_day


def get_stock_name(deal_date):
    return f"""
        SELECT  CODE,
                CASE WHEN NAME LIKE ('*%') THEN SUBSTR(NAME , 2)
                ELSE NAME END AS NAME
        FROM    (
                    SELECT  DATEDEAL, CODE, NAME
                    FROM    TP_STOCK.KOSPI_MASTER
                    WHERE   DATEDEAL = '{deal_date}'
                    UNION
                    SELECT  DATEDEAL, CODE, NAME
                    FROM    TP_STOCK.KOSDAQ_MASTER
                    WHERE   DATEDEAL = '{deal_date}'
                )
    """


def get_cybos7210(subject, sort, deal_date, time_deal):
    return f"""
        SELECT  ROW_NUMBER() OVER(ORDER BY {subject} {sort}) AS RANK,
                STKCODE,
                TIMEDEAL,
                FORR,
                ORGR,
                ORG3,
                ORG6,
                DODRATIO
            FROM
                    (
                        SELECT  STKCODE, 
                                TIMEDEAL,
                                FORR,
                                ORGR,
                                ORG3,
                                ORG6,
                                DODRATIO
                        FROM    CYBOS_CPSVR7210
                        WHERE   DATEDEAL = '{deal_date}'
                                AND TIMEDEAL LIKE '{time_deal}%'
                        order by {subject} {sort}
                                )
                        )
                """