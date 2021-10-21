def get_html(table, day_html, info_html, week):
    html = f"""
        <div class="right">
            <div class="module-content">
                <div class="module-tbl mt-20">
                    <div class="half-table-box">
                        <div>
                            <table class="table module-table module-table-sm module-table-hover module-table-empty">
                                <colgroup>    
                                    <col width="12%">
                                    <col width="*">
                                    <col width="25%">
                                    <col width="25%">
                                </colgroup>
                                <thead>
                                    <tr>
                                        <th scope="col">순위</th>
                                        <th scope="col">종목</th>
                                        <th scope="col">목표가</th>
                                        <th scope="col" class="btl">현재가대비*</th>
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
                                    <col width="12%">
                                    <col width="*">
                                    <col width="25%">
                                    <col width="25%">
                                </colgroup>
                                <thead>
                                    <tr>
                                        <th scope="col">순위</th>
                                        <th scope="col">종목</th>
                                        <th scope="col">목표가</th>
                                        <th scope="col" class="btl">현재가대비*</th>
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
                        <span class="pull-right">
                                    * 현재가는 {week} 종가 기준임
                        </span>
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
                             <span>{r['goal_value']}</span>
                        </td>
                        <td class="text-center btl">
                             <span>{r['gap_ratio']}%</span>
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
                             <span>{r['goal_value']}</span>
                        </td>
                        <td class="text-center btl">
                             <span>{r['gap_ratio']}%</span>
                        </td>
                    </tr>
                        """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    return collect


def get_info_html(info):
    sent = """"""
    for r in info:
        sent += f"""
            <a href="#" class="obj obj-popover" data-container="body" data-toggle="popover"
                            title="" data-content="'{r['cont_a']}'" data-original-title="{r['datedeal']} ({r['org_name']})"></a>
                """
    return sent


def get_day_html(days):
    day = """"""
    for r in days:
        day += f"""
            <span>
            ({r['datedeal_5']} ~{r['datedeal_1']} 발표기준)
            </span>
                """
    return day
