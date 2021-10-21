import datetime
from adm.jobs import (
                        get_time_period,
                        get_previous_day
                        )


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


def get_cybos7254(subject, dealing_type, sort, deal_date):
    return f"""
        SELECT  X.STKCODE,                                
                X.FOR_SONMEME_AMT,
                X.ORG_SONMEME_AMT,
                X.ETC_SONMEME_AMT,
                X.ORG_SONMEME_CNT,
                X.ORG_MESU_CNT,
                X.ORG_MEDO_CNT,
                X.ORG3_SONMEME_CNT,
                X.ORG3_MESU_CNT,
                X.ORG3_MEDO_CNT,
                X.ORG6_SONMEME_CNT,
                X.ORG6_MESU_CNT,
                X.ORG6_MEDO_CNT,
                X.ORG9_SONMEME_CNT,
                X.ORG9_MESU_CNT,
                X.ORG9_MEDO_CNT,                
                ORG3_SONMEME_AMT,
                ORG6_SONMEME_AMT,
                ORG9_SONMEME_AMT,
                ROW_NUMBER() OVER(ORDER BY X.{subject}_{dealing_type} {sort}) AS RANK
        FROM    (
                    SELECT  DATEDEAL,
                            STKCODE,                            
                            FOR_SONMEME_AMT,
                            ORG_SONMEME_AMT,                            
                            ETC_SONMEME_AMT,
                            ORG_SONMEME_CNT,
                            ORG_MESU_CNT,
                            ORG_MEDO_CNT,
                            ORG3_SONMEME_CNT,
                            ORG3_MESU_CNT,
                            ORG3_MEDO_CNT,
                            ORG6_SONMEME_CNT,
                            ORG6_MESU_CNT,
                            ORG6_MEDO_CNT,
                            ORG9_SONMEME_CNT,
                            ORG9_MESU_CNT,
                            ORG9_MEDO_CNT,
                            ORG3_SONMEME_AMT,
                            ORG6_SONMEME_AMT,
                            ORG9_SONMEME_AMT
                    FROM    CYBOS_CPSVR7254
                    WHERE   DATEDEAL = '{deal_date}'
                    ORDER BY {subject}_{dealing_type} {sort}
                ) X
    """


def get_cybos7210(subject, sort, deal_date, time_deal):
    return f"""
            SELECT  ROW_NUMBER() OVER(ORDER BY {subject}_amt {sort}) AS RANK,
                    STKCODE,
                    TIMEDEAL,
                    FORR_AMT,
                    ORGR_AMT,
                    ORG3_AMT,
                    ORG6_AMT
            FROM
                    (
                        SELECT  STKCODE,                                
                                TIMEDEAL,
                                FORR_AMT,
                                ORGR_AMT,
                                ORG3_AMT,
                                ORG6_AMT
                        FROM    CYBOS_CPSVR7210
                        WHERE   DATEDEAL = '{deal_date}'
                                AND TIMEDEAL LIKE '{time_deal}%'
                        ORDER BY  {subject}_amt {sort}
                    )
            """

def get_amt_theme(subject, unit, theme_code, deal_date, count):
        return f"""
            SELECT  A.DATEDEAL, SUM(A.{subject}_SONMEME_{unit}) AS AMT
            FROM    RC_TEAM.cybos_cpsvr7254 A
                    , (
                            SELECT  STKCODE
                            FROM    RC_TEAM.EBEST_THEME_MAPPING
                            WHERE   THEMECODE = {theme_code}
                                    AND DATEDEAL ='{deal_date}'
                    ) B
                    , (
                            SELECT  DATEDEAL
                            FROM    (
                                        SELECT  DATEDEAL
                                        FROM    TRADE_DAY
                                        WHERE   DATEDEAL <= '{deal_date}'
                                        ORDER BY DATEDEAL DESC
                                    ) A
                            WHERE   ROWNUM <= {count}
                    ) C
            WHERE   A.STKCODE = B.STKCODE
                    AND  A.DATEDEAL = C.DATEDEAL
            GROUP BY A.DATEDEAL
            ORDER BY A.DATEDEAL DESC
            """

def get_amt_iss(subject, unit, issn, deal_date, count):        
        return f"""
            SELECT  A.DATEDEAL, SUM(A.{subject}_SONMEME_{unit}) AS AMT
            FROM    RC_TEAM.cybos_cpsvr7254 A
                    , (
                            select  code                                            
                            from    KTP.ct_issue_code
                            where   issn = '{issn}'
                    ) B
                    , (
                            SELECT  DATEDEAL
                            FROM    (
                                        SELECT  DATEDEAL
                                        FROM    TRADE_DAY
                                        WHERE   DATEDEAL <= '{deal_date}'
                                        ORDER BY DATEDEAL DESC
                                    ) A
                            WHERE   ROWNUM <= {count}
                    ) C
            WHERE   A.STKCODE = B.CODE
                    AND  A.DATEDEAL = C.DATEDEAL
            GROUP BY A.DATEDEAL
            ORDER BY A.DATEDEAL DESC
            """

def get_before_hour(now_datetime, before):        
    current = datetime.datetime.strptime(now_datetime, "%Y%m%d%H%M%S")
    before_hour = current - datetime.timedelta(hours=before)
    return before_hour.strftime("%H")


def get_before_day(today: str, hour_period: str, now_datetime, before):        
        a = get_before_hour(now_datetime, before)
        a = int(a)
        if hour_period == '1_BEFORE_TRADE':                
                if a > 8:                        
                        date = datetime.datetime.strptime(today, "%Y%m%d")
                        before_day = date - datetime.timedelta(days=1)                        
                        return before_day.strftime("%Y%m%d")
                else:
                        return today                        
        elif hour_period == '2_TRADE_AM':                
                if a > 11:
                        date = datetime.datetime.strptime(today, "%Y%m%d")
                        before_day = date - datetime.timedelta(days=1)                        
                        return before_day.strftime("%Y%m%d")
                else:
                        return today
        elif hour_period == '3_TRADE_PM':                
                if a > 15:
                        date = datetime.datetime.strptime(today, "%Y%m%d")
                        before_day = date - datetime.timedelta(days=1)                        
                        return before_day.strftime("%Y%m%d")
                else:
                        return today
        elif hour_period == '4_AFTER_TRADE':                
                if a > 19:
                        date = datetime.datetime.strptime(today, "%Y%m%d")
                        before_day = date - datetime.timedelta(days=1)                        
                        return before_day.strftime("%Y%m%d")
                else:
                        return today
        else:
                return today          


def get_empty_hour(deal_date: str, hour_period:str, now:str, hh:str)->str:
        """
                now is expressed as %Y%m%d%H%M as a string
                deal_date is expressed as %Y%m%d as a string
                hh is expressed about hour like %H as a string
        """        
        return f"""
        (
                SELECT  '{get_before_day(deal_date, hour_period, now, 23)}' || '{get_before_hour(now, 23)}' AS YYYYMMDDHH FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 22)}' || '{get_before_hour(now, 22)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 21)}' || '{get_before_hour(now, 21)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 20)}' || '{get_before_hour(now, 20)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 19)}' || '{get_before_hour(now, 19)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 18)}' || '{get_before_hour(now, 18)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 17)}' || '{get_before_hour(now, 17)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 16)}' || '{get_before_hour(now, 16)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 15)}' || '{get_before_hour(now, 15)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 14)}' || '{get_before_hour(now, 14)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 13)}' || '{get_before_hour(now, 13)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 12)}' || '{get_before_hour(now, 12)}' FROM DUAL UNION ALL                                                
                SELECT  '{get_before_day(deal_date, hour_period, now, 11)}' || '{get_before_hour(now, 11)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 10)}' || '{get_before_hour(now, 10)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 9)}' || '{get_before_hour(now, 9)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 8)}' || '{get_before_hour(now, 8)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 7)}' || '{get_before_hour(now, 7)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 6)}' || '{get_before_hour(now, 6)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 5)}' || '{get_before_hour(now, 5)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 4)}' || '{get_before_hour(now, 4)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 3)}' || '{get_before_hour(now, 3)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 2)}' || '{get_before_hour(now, 2)}' FROM DUAL UNION ALL
                SELECT  '{get_before_day(deal_date, hour_period, now, 1)}' || '{get_before_hour(now, 1)}' FROM DUAL UNION ALL
                SELECT  '{deal_date}' || '{hh}' FROM DUAL
        ) A
    """

def related_stock(column, analysis_type, deal_date, condition, num):
        return f"""
            select  *
            from    (
                        SELECT  {', '.join(column)}
                        FROM    {analysis_type} 
                        WHERE   DATEDEAL = '{deal_date}'
                        {condition}
                    )
            where   rownum <= {num}
            """      

def get_sorting(**rows):    
        def sorting(row):
            L = []
            for r in row:                
                L.append(row[r])
            return L 
        L = []        
        for i, r in enumerate(rows):
            a = sorting(rows[r])
            if i == 0:
                continue
            L.extend(a)
        x = selectionsort(L)        
        return [x[0], x[-1]]
                
def selectionsort(x):
    length = len(x)
    for i in range(length-1):
        indexmin = i
        for j in range(i+1, length):
            if x[indexmin] > x[j]:
                indexmin = j
        x[i], x[indexmin] = x[indexmin], x[i]
    return x
        
def get_trend_value(issn, deal_date):
        return f"""
            select  B.DATEDEAL,
                    NVL(A.TREND, 0) AS TREND
            from    (
                        SELECT  DATEDEAL,
                                TREND
                        FROM    RC_TEAM.DATA_NAVER_TREND_1M
                        WHERE   ISSN = '{issn}'
                     )A,                     
                    (
                        SELECT  DATEDEAL                                
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{deal_date}'--yesterday
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= 20 --Fixme
                    )B
            where   B.DATEDEAL = A.DATEDEAL(+)
            order by  b.datedeal asc
            """

def get_stock_related(issn, count):
        return f"""
            select  code
            from    (
                        select  a.code,
                                b.fluct_ratio
                        from    KTP.ct_issue_code a,
                                a3_curprice b
                        where   issn = '{issn}'
                        and     a.code = b.stk_code
                        order by fluct_ratio desc
                    )
            where rownum<={count}
            """