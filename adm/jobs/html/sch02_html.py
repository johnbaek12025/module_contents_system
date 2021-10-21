def get_html(table):
    html = f"""
        <div class="module-tbl-txt">
            <span">투자자 검색 상위 종목</span>
        </div>
        <!-- //txt -->

        <div class="module-tbl">
            <div class="third-table-box">
                <div>
                    <table class="table module-table module-table-sm">
                        <colgroup>    
                            <col width="20%">
                            <col width="*%">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">상위연속</th>
                            </tr>
                        </thead>
                        <tbody>        
                            {table[0]}
                        </tbody>
                    </table>
                </div>
                <!-- // width=1/3 -->

                <div>
                    <table class="table module-table module-table-sm">
                        <colgroup>    
                            <col width="20%">
                            <col width="*%">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">상위연속</th>
                            </tr>
                        </thead>
                        <tbody>        
                            {table[1]}
                        </tbody>
                    </table>
                </div>
                <!-- // width=1/3 -->
                <div>
                    <table class="table module-table module-table-sm">
                        <colgroup>    
                            <col width="20%">
                            <col width="*%">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">상위연속</th>
                            </tr>
                        </thead>
                        <tbody>        
                            {table[2]}
                        </tbody>
                    </table>
                </div>
                <!-- //tbl -->
                <div class="module-tbl-txt mt-10">
                <span class ="pull-left">※ 상위연속 : 투자자 검색 상위 30위 이내에 연속적으로 랭킹된 일수</span>    
                </div>



     """
    return html


def get_table(rows):
    collect = []
    table = """"""
    k = 'class = "active"'
    j = 0

    for i in rows:

        rank_period_len = i["rank_period_len"]

        if rank_period_len >= 5:
            rank_period_len_str = str(rank_period_len)

        else:
            rank_period_len_str = str("-")

        if i["rank"] > 15:

            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{i['rank']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['stock_name']}</span>
                        </td>
                        <td class="text-center">
                            <span>{rank_period_len_str}</span>
                        </td>
                    </tr>
                    """
        else:
            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{i['rank']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['stock_name']}</span>
                        </td>
                        <td class="text-center">
                             <span>{rank_period_len_str}</span>
                        </td>
                    </tr>
                    """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    # print(collect)
    return collect
