def get_html(rows, down):
    html = f"""
       <div class="module-content">
    <div class="module-tbl-txt">
        <button type="button" class="pull-right">공시 원본 보기</button>
    </div>
    <!-- //guide -->
    <div class="module-tbl mt-10">
        <table class="table module-table">
            <colgroup>
                <col width="20%">
                <col width="*">
            </colgroup>
            <tbody>
                <tr>
                    <th class="text-center">
                        계 약 명
                    </th>
                    <td>
                        <span class="fw500">{rows['suju_cont']}</span>
                    </td>
                </tr>
                <tr>
                    <th class="text-center">
                        계약금액
                    </th>
                    <td>
                        <span>
                            {rows['amount']} 억원 <em class="up">(매출액 대비 {rows['sales_portion']}%)</em>
                        </span>
                    </td>
                </tr>
                <tr>
                    <th class="text-center">
                        계약상대
                    </th>
                    <td>
                        <span>{rows['partner_name']}</span>
                    </td>
                </tr>
                <tr>
                    <th class="text-center">
                        계약기간
                    </th>
                    <td>
                        <span>{rows['start_dt']}~{rows['end_dt']}</span>
                    </td>
                </tr>
                <tr>
                    <th class="text-center">
                        계약일자
                    </th>
                    <td>
                        <span>{rows['contract_date']}</span>
                    </td>
                </tr>
            </tbody>
        </table>
        <!-- //table -->
    </div>
    <!-- //tbl -->
    {down}
    </div>
        """
    return html


def get_row_html(rows):
    html = ""
    for r in rows:
        html += f"<span class='int'>{r}</span>"
    return f"""
        <div class="module-tbl-txt mt-10">
        <div class="dot">
            최근 계약 체결 공시            
            {html}
        </div>            
        <a href="#" class="pull-right">→ 더보기</a>
    </div>
    <!-- //txt -->
        """
