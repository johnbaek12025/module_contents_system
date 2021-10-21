def get_html(subject, dealing_type, table, info):
    html = f"""
    <div class="module-content">    
        <div class="module-tbl-txt">
            <strong class="title">{subject} {dealing_type} 상위 종목</strong>
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
                                <th scope="col">{dealing_type}금액</th>
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
                                <th scope="col">{dealing_type}금액</th>
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
                                <th scope="col">{dealing_type}금액</th>
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
        <!-- //tbl -->

        <div class="module-tbl-guide mt-20">
            <span>(단위 백만원)</span>
        </div>
        <!-- //guide -->

        <div class="module-tbl-txt mt-10">
            <div class="dot">{info}</div>
        </div>
         </div>
            <!-- //module-content -->   
    """
    return html


def get_table(rows):
    collect = []
    table = """"""
    k = 'class = "active"'
    j = 0
    for i in rows:
        if i["rank"] > 15:
            table += f"""
                    <tr {k}>
                        <td class="text-center">
                            <span>{i['rank']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['stkname']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['amount']}</span>
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
                            <span>{i['stkname']}</span>
                        </td>
                        <td class="text-center">
                            <span>{i['amount']}</span>
                        </td>
                    </tr>
                    """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    return collect
