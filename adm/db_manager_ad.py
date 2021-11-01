import adm.db_manager
from adm import remove_empty_between_tag
from adm.jobs import subject_7254
from adm.exceptions import ConfigError, ContentsError

# 콘텐츠 생성하는 것에 대해 공통적으로 사용하는 query
class DBManager(adm.db_manager.DBManager):
    def __init__(self):
        pass

    def get_news_seq(self):
        sql = """
            SELECT  NEWS_USER.RTBL_NEWS_SEQUENCE.NEXTVAL
            FROM    DUAL
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return None
        return rows[0][0]

    def get_additional_news_info(self, data_code):
        sql = f"""
            SELECT  NEWS_TYPE, NEWS_DESC
            FROM    ALS_MASTER_DATACODE
            WHERE   DATA_CODE = '{data_code}'
        """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        row = rows[0]
        x["news_type"] = row[0]
        x["news_desc"] = row[1]
        return x

    def get_stock_list_from_analysis_table(
        self,
        analysis_type,
        deal_date,
        dealing_type,
        subject,
        market_type,
        sort_by,
        sort_order,
        count=3,
    ):
        if market_type is None:
            market_type_condition = ""
        else:
            market_type_condition = f"AND     MARKET = {market_type}"
        sql = f"""
            SELECT  STK_NAME
            FROM    (
                        SELECT  STK_NAME
                        FROM    {analysis_type}
                        WHERE   DATEDEAL = '{deal_date}'
                        AND     SONMEME_TYPE = '{dealing_type.upper()}'
                        AND     CUSTOMER_TYPE = '{subject.upper()}'
                        {market_type_condition}
                        ORDER BY {sort_by} {sort_order}
                    ) A
            WHERE   ROWNUM <= {count}
        """
        rows = self.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            x.append(r[0])
        return x

    def get_7254_ts_data(self,
                         stock_code,
                         subject,
                         dealing_type,
                         unit,
                         deal_date,
                         count=1):
        sql = f"""
            SELECT  A.DATEDEAL, {subject}_{dealing_type}_{unit}
            FROM    CYBOS_CPSVR7254 A
                    , (
                        SELECT  DATEDEAL
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{deal_date}'
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= {count}
                    ) B                
            WHERE   A.STKCODE = '{stock_code}'
            AND     A.DATEDEAL = B.DATEDEAL
            ORDER BY A.DATEDEAL
        """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def get_topics(self, news_code):
        sql = f"""            
            SELECT  CNL_CODE
            FROM    RTBL_LUP_NPC_NEW
            WHERE   NEWS_CODE = '{news_code}'
        """
        rows = self.get_all_rows(sql)
        x = []
        for r in rows:
            x.append(r[0])
        return x

    def get_7254_value(self, deal_date, stock_code, subject, dealing_type,
                       unit):
        col_name = f"{subject}_{dealing_type}_{unit}"
        sql = f"""
            SELECT  A.{col_name}
            FROM    CYBOS_CPSVR7254 A
            WHERE  A.DATEDEAL = '{deal_date}'
            AND    A.STKCODE  = '{stock_code}'
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return None
        return rows[0][0]

    def get_7254_accu_value(self,
                            deal_date,
                            stock_code,
                            dealing_type,
                            unit,
                            accumulated_days=1):
        """
        accumulated_days 를 1로 세팅하면, CYBOS_CPSVR7254에서 지정된 날짜의 값만 전달됨
        """
        cols = [f"{i}_{dealing_type}_{unit}" for i in subject_7254]
        select_targt = ", ".join(f"SUM(A.{i}) AS {i}" for i in cols)
        sql = f"""
            SELECT  {select_targt}
            FROM    CYBOS_CPSVR7254 A
                    , (
                        SELECT  DATEDEAL
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{deal_date}'
                                    ORDER BY DATEDEAL DESC
                                ) A
                        WHERE   ROWNUM <= {accumulated_days}
                    ) B
            WHERE  A.DATEDEAL = B.DATEDEAL
            AND    A.STKCODE  = '{stock_code}'
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return None
        row = rows[0]
        return_dict = {}
        for n, i in enumerate(subject_7254):
            return_dict[i] = row[n]
        return return_dict

    def get_dates(self, deal_date, count, order='desc'):
        sql = f"""
            select  *
            from    (
                        SELECT  DATEDEAL
                        FROM    (
                                    SELECT  DATEDEAL
                                    FROM    TRADE_DAY
                                    WHERE   DATEDEAL <= '{deal_date}'
                                    ORDER BY DATEDEAL desc
                                ) A
                        WHERE   ROWNUM <= {count}
                    )
            order by datedeal {order}
            """
        row = self.get_all_rows(sql)
        x = []
        if not row:
            return x
        for r in row:
            x.append(r[0])
        return x

    def get_master_info(self, deal_date, stock_code):
        sql = f"""
            SELECT  CODE, NAME, TOTSTOCK * 1000
            FROM    (
                        SELECT  CODE, NAME, TOTSTOCK
                        FROM    TP_STOCK.KOSPI_MASTER
                        WHERE   DATEDEAL = '{deal_date}'
                        AND     CODE     = '{stock_code}'
                        UNION -- 혹시 몰라서...
                        SELECT  CODE, NAME, TOTSTOCK
                        FROM    TP_STOCK.KOSDAQ_MASTER
                        WHERE   DATEDEAL = '{deal_date}'
                        AND     CODE     = '{stock_code}'
                    ) A
            """
        rows = self.get_all_rows(sql)
        if not rows:
            return None
        row = rows[0]

        return {
            "code": row[0],
            "name": row[1],
            "total_stock": row[2],
        }

    def get_report(self, datedeal, stock_code, count, sort_order="ASC"):
        sql = f"""
            SELECT  A.DATEDEAL, B.ORG_NAME, A.CONT_A, A.GOAL_VALUE, A.OPINION_CODE
            FROM    (
                        SELECT  DATEDEAL, CONT_A, ORG_CODE, GOAL_VALUE, OPINION_CODE
                        FROM    TP_STOCK.ORG_OPINION_MANUAL_MOD
                        WHERE   DATEDEAL <= '{datedeal}'
                        AND     CODE = '{stock_code}'
                        ORDER BY DATEDEAL DESC, ORG_CODE ASC
                    ) A
                    , TP_STOCK.STOCK_CHANGKU_CODE B
            WHERE   A.ORG_CODE = B.ORG_NUM
            AND     ROWNUM <= {count}
            ORDER BY A.DATEDEAL {sort_order}
        """
        rows = self.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            row = {
                "deal_date": r[0],
                "stock_firm": r[1],
                "title": r[2],
                "goal_value": r[3],
                "opinion_code": int(r[4]),
            }
            x.append(row)
        return x

    def get_related_stock_theme(self, theme_code, deal_date, count):
        sql = f"""
            SELECT  code--STK_CODE
            FROM    (
                        SELECT  a.code,--A.STK_CODE,
                                B.DATEDEAL,
                                a.ratio--A.FLUCT_RATIO
                        FROM    stock_1_day a,--A3_CURPRICE A, --FIXME it must be changed later to a3_curprice
                                (           
                                    SELECT  B.DATEDEAL,
                                            B.STKCODE                                
                                    FROM    RC_TEAM.EBEST_THEME_MAPPING B                    
                                    WHERE   B.THEMECODE = '{theme_code}'
                                    AND     B.DATEDEAL = {deal_date} 
                                )B
                        WHERE   B.STKCODE = a.code --B.STKCODE = A.STK_CODE
                        AND     B.DATEDEAL = a.datedeal --B.DATEDEAL = A.D_CNTR
                        ORDER BY a.ratio desc --A.FLUCT_RATIO DESC
                    )
            where   ROWNUM<={count}
            """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            name = self.get_master_info(deal_date, r[0])
            id = name['name']
            x[id] = r[0]
        return x

    def get_org_ktp_relation(self, subject, dealing_type, unit, order, issn,
                             deal_date, count):
        sql = f"""
            SELECT  STKCODE        
            FROM    (
                        SELECT  ROW_NUMBER() OVER(ORDER BY A.{subject}_{dealing_type}_{unit} {order}) AS RANK,        
                                A.DATEDEAL, 
                                A.STKCODE                                
                        FROM    RC_TEAM.cybos_cpsvr7254 A
                                , (
                                    select  code                                            
                                    from    KTP.ct_issue_code
                                    where   issn = '{issn}'
                                ) B
                        WHERE   A.STKCODE = B.CODE 
                        AND     A.DATEDEAL = '{deal_date}'
                        ORDER BY  RANK ASC
                    )
            where rownum<={count}            
            """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            name = self.get_master_info(deal_date, r[0])
            id = name["name"]
            x[id] = r[0]
        return x

    def get_essential_info_data(self,
                                analysis_type,
                                table_name: list,
                                deal_date,
                                sn,
                                condition=""):
        """
        I added a partition for conditions in the part of the sql
        so if you need any condition for sql  you can isert condition
        like 'where something = 'str''
        """
        cols = [f"{col}" for col in table_name]
        sql = f"""
            SELECT  {', '.join(cols)}
            FROM    {analysis_type} 
            WHERE   DATEDEAL = '{deal_date}'
            AND     INFO_SEQ = {sn}            
            {condition}
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return None
        row = rows[0]
        return_dict = {}
        for n, i in enumerate(table_name):
            return_dict[i] = row[n]
        return return_dict

    def get_stock_info(self,
                       deal_date,
                       count,
                       stock_code,
                       price=False,
                       ratio=False,
                       vol=False,
                       order='asc'):
        """
        This method is for getting information with stock_code and deal_date
        about price or ratio of previous day
        but you should consider about the information is about in market or after market
        because this is for after market information
        if you want to get inforamation in market you should make it on your own.
        """
        if price is True:
            x = ["A.JONGGA"]
        elif ratio is True:
            x = ["A.RATIO"]
        elif vol is True:
            x = ["A.VOL"]
        elif price is True and ratio is True:
            x = ["A.JONGGA", "A.RATIO"]

        sql = f"""
                SELECT  A.DATEDEAL,
                        {', '.join(x)}
                FROM    STOCK_1_DAY A,
                        (
                            SELECT  DATEDEAL
                            FROM    (
                                        SELECT  DATEDEAL
                                        FROM    TRADE_DAY
                                        WHERE   DATEDEAL <= '{deal_date}'
                                        ORDER BY DATEDEAL desc
                                    ) A
                            WHERE   ROWNUM <= {count}
                        )B
                WHERE   A.DATEDEAL = B.DATEDEAL
                AND     A.CODE = '{stock_code}'
                order by  a.datedeal {order}
            """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            id = r[0]
            x[id] = r[1]
        return x

    def get_related_stock(self, issn, count, deal_date, order='desc'):
        sql = f"""
            select  code
            from    (
                        select  a.code,
                                b.stk_name,
                                b.fluct_ratio
                        from    KTP.ct_issue_code a,
                                a3_curprice b
                        where   issn = '{issn}'
                        and     a.code = b.stk_code
                        order by fluct_ratio {order}
                    )
            where rownum<={count}
            """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            name = self.get_master_info(deal_date, r[0])
            if not name:
                continue
            id = name.get('name')
            x[id] = r[0]
        return x

    def get_pre_related_stock(self, issn, count, deal_date, order='desc'):
        sql = f"""
            select  code
            from    (
                        select  a.code,                                
                                max(b.ratio) as ratio
                        from    KTP.ct_issue_code a,
                                stock_1_day b
                        where   issn = '{issn}'
                        and     a.code = b.code
                        group  by  a.code
                        order by ratio {order}
                    )
            where rownum<={count}
            """
        rows = self.get_all_rows(sql)
        x = {}
        if not rows:
            return x
        for r in rows:
            name = self.get_master_info(deal_date, r[0])
            id = name.get("name")
            x[id] = r[0]
        return x

    def save_news_info(self, d, commit=True):
        sql = f"""
            INSERT INTO RTBL_NEWS_INFO ( -- 뉴스정보
                NEWS_SN         -- 뉴스SN
                , D_NEWS_CRT    -- 뉴스생성일자
                , T_NEWS_CRT    -- 뉴스생성시간
                , NEWS_CODE     -- 뉴스코드    
                , STK_CODE      -- 단축종목코드
                , NEWS_TITLE    -- 뉴스제목
                , NEWS_INP_KIND -- 뉴스입력종류 (I: Insert, U: Update, D: Delete)
                , IS_MANUAL     -- 수동처리여부, 수동입력된 경우 1
                , RSV_NEWS_YN   -- 예약뉴스여부
                , ORI_NEWS_SN     -- 원본뉴스SN
                , D_ORI_NEWS_CRT  -- 원본뉴스생성일자

           ) VALUES (
                '{d.news_seq}'
                , '{d.now_date}' 
                , '{d.now_time}' 
                , '{d.news_code.upper()}' 
                , '{d.stock_code}'
                , '{d.news_title}'
                , '{d.request_type}' 
                , '{d.is_manual}' 
                , '{d.is_reserved}' 
                , {'Null' if d.org_news_seq is None else d.org_news_seq} 
                , {'Null' if d.org_now_date is None else d.org_now_date}           
            )     
        """
        self.modify(sql, commit)

    def save_news_cnts(self, d, commit=True):
        news_cnts = remove_empty_between_tag(d.news_cnts)
        sql = f"""
            INSERT INTO RTBL_NEWS_CNTS_ATYPE ( -- 뉴스본문-ATYPE
                NEWS_SN,         -- 뉴스SN
                D_NEWS_CRT,      -- 뉴스생성일자               
                CNTS_TYPE,       -- 뉴스형태 (T:Text, H:Html, I:Image, A:Audio, V:Video, N:Nothing)
                D_NEWS_CNTS_CRT, -- 뉴스본문생성일자
                T_NEWS_CNTS_CRT, -- 뉴스본문생성시간
                NEWS_CNTS,       -- 뉴스본문
                NEWS_CODE,       -- 뉴스코드
                RPST_IMG_URL     -- 대표이미지URL (없을 경우, N)
            ) VALUES (
                '{d.news_seq}', 
                '{d.now_date}',                
                '{d.contents_type}',  
                '{d.now_date}', 
                '{d.now_time}', 
                '{news_cnts}', 
                '{d.news_code.upper()}',
                '{d.rep_image}'         
            )
        """
        self.modify(sql, commit)

    def save_news_com(self, d, commit=True):
        sql = f"""
            INSERT INTO RTBL_COM_ALS_INFOSN ( 
                SN
                , D_CRT
                , INFO_SN
                , INFO_CODE
            ) VALUES (
                '{d.news_seq}'
                , '{d.now_date}'
                , '{d.info_seq}'
                , '{d.info_code}'
            )
        """
        self.modify(sql, commit)

    def get_requests(self, count=10):
        sql = f"""
            SELECT  B.SN
                    , B.TYPE
                    , B.INFO_CODE
                    , B.DATEDEAL
                    , B.IS_MANUAL
            FROM    (
                        SELECT  A.SN
                                , ROW_NUMBER() OVER (ORDER BY A.DT_CRT ASC) RN
                        FROM    ALS_COM_CNL A                    
                        WHERE   A.CHANNEL = 'TpTpC1'
                        AND     A.STATUS  = 'N'
                    ) A
                    , ALS_MAIN B
            WHERE   A.RN <= {count}
            AND     A.SN = B.SN
        """
        rows = self.get_all_rows(sql)
        x = []
        if not rows:
            return x
        for r in rows:
            info_code = r[2]
            info_code = info_code.lower()
            row = {
                "info_seq": r[0],
                "request_type": r[1],
                "info_code": info_code,
                "deal_date": r[3],
                "is_manual": r[4],
            }
            x.append(row)
        return x

    def handle_processed_requests(self, info_seq):
        # 생성된 콘텐츠에 대한 update
        self.change_requests_status(info_seq)
        self.move_requests()
        self.delete_requests()

    def change_requests_status(self, info_seq, status="S", commit=True):
        sql = f"""
            UPDATE ALS_COM_CNL
            SET    STATUS = '{status}'
            WHERE  SN = {info_seq}
        """
        self.modify(sql, commit)

    def move_requests(self):
        pass

    def delete_requests(self):
        pass

    def get_original_data(self, info_seq):
        sql = f"""
            SELECT  NEWS_SN, D_NEWS_CRT, STK_CODE, NEWS_TITLE, NEWS_CODE
            FROM    RTBL_NEWS_INFO A
                    , (
                        SELECT  A.D_CRT, A.SN
                        FROM    (
                                    SELECT  A.D_CRT 
                                            , A.SN
                                            , ROW_NUMBER() OVER (ORDER BY A.D_CRT DESC, A.SN DESC) RN
                                    FROM    RTBL_COM_ALS_INFOSN A
                                    WHERE   A.INFO_SN = {info_seq}
                                ) A
                        WHERE   RN = 1
                    ) B
            WHERE   A.NEWS_SN = B.SN
            AND     A.D_NEWS_CRT  = B.D_CRT
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return {}
        row = rows[0]
        return {
            "news_seq": row[0],
            "news_date": row[1],
            "stock_code": row[2],
            "news_title": row[3],
            "news_code": row[4],
        }

    def check_if_exist_in_als_main(self,
                                   deal_date,
                                   info_code,
                                   stock_code=None,
                                   theme_code=None,
                                   issn=None):
        if stock_code is None:
            stock_condition = ""
        else:
            stock_condition = f"AND  A.STK_CODE ='{stock_code}'"

        if theme_code is None:
            theme_condition = ""
        else:
            theme_condition = f"AND  A.THEME_CODE ='{theme_code}'"

        if issn is None:
            issn_condition = ""
        else:
            issn_condition = f"AND  A.ISSN ='{issn}'"

        sql = f"""
            SELECT  COUNT(*)
            FROM    ALS_MAIN A
            WHERE   A.DATEDEAL  = '{deal_date}'
            AND     A.INFO_CODE = '{info_code}'
            AND     A.TYPE      = 'I'
            {stock_condition}
            {theme_condition}
            {issn_condition}
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return 0
        return rows[0][0]

    def get_lastest_infosn(self, deal_date, info_code, stock_code, theme_code,
                           issn):
        if stock_code is None:
            stock_condition = ""
        else:
            stock_condition = f"AND  A.STK_CODE ='{stock_code}'"

        if theme_code is None:
            theme_condition = ""
        else:
            theme_condition = f"AND  A.THEME_CODE ='{theme_code}'"

        if issn is None:
            issn_condition = ""
        else:
            issn_condition = f"AND  A.ISSN ='{issn}'"

        sql = f"""
            SELECT  MAX(D_CRT) AS D_CRT
                    , MAX(SN) AS SN
            FROM    NEWS_USER.RTBL_COM_ALS_INFOSN A
                    , (
                        SELECT  MAX(SN) AS AM_SN
                        FROM    ALS_MAIN A
                        WHERE   A.DATEDEAL   = '{deal_date}'
                        AND     A.INFO_CODE  = '{info_code}'
                        {stock_condition}
                        {theme_condition}
                        {issn_condition}
                    ) B
            WHERE   A.INFO_SN = B.AM_SN
            AND     A.D_CRT = '{deal_date}'
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return {}
        row = rows[0]
        return {
            "news_date": row[0],
            "news_seq": row[1],
        }

    def get_lastest_infosn_for_gongsi(self, rcpno):
        sql = f"""
            SELECT  MAX(D_CRT) AS D_CRT
                    , MAX(SN) AS SN
            FROM    NEWS_USER.RTBL_COM_ALS_INFOSN A                   
            WHERE   A.INFO_SN = {rcpno}
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return {}
        row = rows[0]
        return {
            "news_date": row[0],
            "news_seq": row[1],
        }

    def check_gongsi_condition(self, analysis_type, info_seq, columns):
        sql = f"""            
            SELECT  {', '.join(columns)}
            FROM    {analysis_type}
            WHERE   INFO_SEQ = '{info_seq}'
            -- 오늘 날짜의 데이터를 가져와야 하나???
        """
        rows = self.get_all_rows(sql)
        if not rows:
            return True, {}
        rows = rows[0]
        orircpno = rows[0]
        if len(rows) > 1:
            chicomtp = rows[1]
            if chicomtp is None:
                return True, {}
            else:
                return False, {}

        if orircpno is None:
            return True, {}
        else:
            return False, {}