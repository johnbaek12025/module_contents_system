def get_html(market, table):
    html = f"""
        <div class="module-tbl-txt">
            <span>{market} 관련글 수 상위 종목 </span>
        </div>
        <!-- //txt -->

        <div class="module-tbl">
            <div class="third-table-box">
                <div>
                    <table class="table module-table module-table-sm">
                        <colgroup>
                            <col width="20%">
                            <col width="*">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">관련글수</th>
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
                            <col width="*">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">관련글수</th>
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
                            <col width="*">
                            <col width="33%">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col">순위</th>
                                <th scope="col">종목</th>
                                <th scope="col">관련글수</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table[2]}                                                                                                                
                        </tbody>
                    </table>
                </div>
                <!-- // width=1/3 -->
            </div>
            <!-- //thrid -->
        </div>        
    """
    return html

def get_table(rows):
    collect = []
    table = """"""    
    j = 0
    for i in rows:        
        table += f"""
                <tr>
                    <td class="text-center">
                        <span>{i['rk']}</span>
                    </td>
                    <td class="text-center">
                        <span>{i['stk_name']}</span>
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