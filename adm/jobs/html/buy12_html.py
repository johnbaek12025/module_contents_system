def get_html(subject, dealing_type, date, time, table, info):
    html = f"""
            <div class="module-tbl-txt">
                <strong class="title title-s">{subject} {dealing_type} 상위종목({date}일 {time['time']}기준 잠정집계 )</strong>
            </div>
            <!-- //txt -->
            <div class="module-tbl">
                <div class="half-table-box">
                    <div>
                        <table class="table module-table module-table-sm">
                            <colgroup>
                                <col width="20%">
                                <col width="*">
                                <col width="35%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th scope="col">매수상위</th>
                                    <th scope="col">종목명</th>
                                    <th scope="col">금액</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table[0]}
                            </tbody>
                        </table>
                    </div>
                    <!-- // -->

                    <div>
                        <table class="table module-table module-table-sm">
                            <colgroup>
                                <col width="20%">
                                <col width="*">
                                <col width="35%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th scope="col">매수상위</th>
                                    <th scope="col">종목명</th>
                                    <th scope="col">금액</th>
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

            <div class="module-tbl-guide mt-15">
                <span>(단위 주)</span>
            </div>
            <!-- //guide -->
            <div class="module-tbl-txt mt-10">
                {info[0]}
                {info[1]}
            </div>            
            """
    return html


def get_table(rows):
    table = """"""
    k = 'class="active"'
    collect = []
    j = 0
    for r in rows:
        if r['rank'] > 10:
            table += f"""
                    <tr {k}>
                        <td class="text-center">
                            <span>{r['rank']}</span>
                        </td>
                        <td class="text-center">
                            <span>{r['stkname']}</span>
                        </td>
                        <td class="text-center">
                            <span>{r['amount']}</span>
                        </td>
                    </tr>
                        """
        else:
            table += f"""
                    <tr>
                        <td class="text-center">
                            <span>{r['rank']}</span>
                        </td>
                        <td class="text-center">
                            <span>{r['stkname']}</span>
                        </td>
                        <td class="text-center">
                            <span>{r['amount']}</span>
                        </td>
                    </tr>
                        """
        j += 1
        if j == 5:
            collect.append(table)
            table = """"""
            j = 0
    return collect


def get_for_info(info, date, time, dealing_type):
    col = []
    for i in info:
        col.append(info[i])
    return f"""<div class="dot">{date}일 {time['time']} {dealing_type}동향: {', '.join(col)}</div>"""


def get_org_info(info):
    if len(info) == 0:
        return ''
    col = []
    for i in info:
        col.append(info[i])
    return f"""<div class="dot">기관 상세 동향: {', '.join(col)}</div>"""