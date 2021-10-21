def get_html(table, info, day_html):
    html = f"""
            <div class="module-tbl mt-20">
                <div class="half-table-box">
                    <div>
                        <table class="table module-table module-table-sm module-table-hover module-table-empty">
                            <colgroup>    
                                <col width="20%">
                                <col width="*">
                                <col width="35%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th scope="col">순위</th>
                                    <th scope="col">종목</th>
                                    <th scope="col">리포트 수량</th>
                                </tr>
                            </thead>
                            <tbody>        
                                {table[0]}
                            </tbody>
                        </table>
                    </div>
                    <!-- // width=1/3 -->

                    <div>
                        <table class="table module-table module-table-sm module-table-hover module-table-empty">
                            <colgroup>    
                                <col width="20%">
                                <col width="*">
                                <col width="35%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th scope="col">순위</th>
                                    <th scope="col">종목</th>
                                    <th scope="col">리포트 수량</th>
                                </tr>
                            </thead>
                            <tbody>        
                                {table[1]}
                            </tbody>
                        </table>
                    </div>
                        <!-- // -->
                    </div>
                        <!-- //half -->
                    </div>
                    <!-- //tbl -->
                    <div class="module-tbl-guide">
                                {day_html}
                    </div>
                    <div class="module-tbl-txt mt-10">
                                {info}
                    </div>


        """
    return html


def get_table(rows):
    collect = []
    table = """"""
    k = 'class = "active"'
    j = 0
    for r in rows:
        if r["rk"] != 10:
            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{r['rk']}</span>
                        </td>
                        <td class="text-center">
                            <a href= "https://dev.thinkpool.com/item/{r['stock_code']}/report" class="obj obj-popover">{r['stock_name']}</a>
                        </td>
                        <td class="text-center">
                             <span>{r['report_cnt']}</span>
                        </td>
                    </tr>
   
                    """
        else:
            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{r['rk']}</span>
                        </td>
                        <td class="text-center">
                            <a href= "https://dev.thinkpool.com/item/{r['stock_code']}/report" class="obj obj-popover">{r['stock_name']}</a>
                        </td>
                        <td class="text-center">
                             <span>{r['report_cnt']}</span>
                        </td>
                    </tr>

                        """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    return collect


def get_info(info):
    sent = """"""
    for r in info:
        sent += f"""
            <div class="dot">{r['datedeal']} ({r['org_name']}) {r['cont_a']}</div>
                """
    return sent


def get_day_html(days):
    day = """"""
    for r in days:
        day += f"""
            <span>
            ({r['start_date_period_len_5']} ~ {r['deal_date']}발표기준)
            </span>
                """
    return day
