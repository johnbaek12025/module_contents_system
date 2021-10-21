def get_html(date, rows, info):
    html = f"""         
           <div class="module-content">       
                 <div class="module-tbl-txt">
                    <strong class="title title-s">{date}일 기관 매매 동향</strong>
                </div>
                <!-- //txt -->

                <div class="module-tbl">
                    <table class="table module-table module-table-bordered">
                        <colgroup>
                            <col width="20%">
                            <col width="20%">
                            <col width="20%">
                            <col width="*">
                        </colgroup>
                        <thead>
                            <tr>
                                <th scope="col"></th>
                                <th scope="col">기관계</th>
                                <th scope="col">투자신탁</th>
                                <th scope="col">연기금</th>
                                <th scope="col">사모펀드</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th scope="row" class="text-right">
                                    <span>순매매</span>
                                </th>
                                <td class="text-right">
                                    <span>{rows['org_net']}</span>
                                </td>
                                <td class="text-right">
                                    <span>{rows['org3_net']}</span>
                                </td>
                                <td class="text-right">
                                    <span>{rows['org6_net']}</span>
                                </td>
                                <td class="text-right">
                                    <span>{rows['org9_net']}</span>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row" class="text-right">
                                    <span>매수</span>
                                </th>
                                <td class="text-right">
                                    <span class = "up">{rows['org_mesu']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "up">{rows['org3_mesu']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "up">{rows['org6_mesu']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "up">{rows['org9_mesu']}</span>
                                </td>
                            </tr>
                            <tr>
                                <th scope="row" class="text-right">
                                    <span>매도</span>
                                </th>
                                <td class="text-right">
                                    <span class = "dn">{rows['org_medo']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "dn">{rows['org3_medo']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "dn">{rows['org6_medo']}</span>
                                </td>
                                <td class="text-right">
                                    <span class = "dn">{rows['org9_medo']}</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <!-- //tbl -->

                <div class="module-tbl-guide mt-15">
                    <span>(단위 주)</span>
                </div>
                <!-- //guide -->

                <div class="module-tbl-txt mt-10">
                    {info}
                </div>

            </div>
            <!-- //module-content -->            
            """
    return html


def get_info(info):
    sent = """"""
    for r in info:
        if 'stock_code' not in r:
            sent += f"""
                <div class="dot">{r['conts']}</div>
                    """
        else:
            sent += f"""
                <div class="dot"><a href=" https://dev.thinkpool.com/item/{r['stock_code']}/report">{r['conts']}</a></div>
                    """
    return sent
