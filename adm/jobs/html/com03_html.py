def get_html(table):
    html = f"""
        <div class="module-tbl-txt">
            <span">코스피 게시물 수 상위 랭킹</span>
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
                                <th scope="col">게시물 수</th>
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
                                <th scope="col">게시물 수</th>
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
                                <th scope="col">게시물 수</th>
                            </tr>
                        </thead>
                        <tbody>        
                            {table[2]}
                        </tbody>
                    </table>
                </div>
     """
    return html


def get_table(rows):
    collect = []
    table = """"""
    k = 'class = "active"'
    j = 0
    for i in rows:
        if i["rk"] > 15:
            table += f"""
                    <tr {k}>
                        <td class="text-center">
                            <span>{i['rk']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['stock_name']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['cnt']}</span>
                        </td>
                    </tr>
                    """
        else:
            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{i['rk']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['stock_name']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['cnt']}</span>
                        </td>
                    </tr>
                    """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    return collect
