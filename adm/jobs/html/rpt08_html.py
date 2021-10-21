def get_html(data):
    html = f"""
        <table class="table module-table mt-20">
            <colgroup>    

                <col width="25%">
                <col width="*">
                <col width="12%">
                <col width="12%">
                <col width="12%">
            </colgroup>
            <thead>
                <tr>
                    <th scope="col">증권사</th>
                    <th scope="col">제목</th>
                    <th scope="col">목표가</th>
                    <th scope="col">변동</th>
                    <th scope="col">발표일</th>
                </tr>
            </thead>
            <tbody>        
                {data}
            </tbody>
        </table>
        """
    return html


def get_row_html(rows):
    html = ""
    for r in rows:
        goal_1 = r["goal_1"]
        goal_2 = r["goal_2"]

        if goal_1 > goal_2:
            change_str = f'<span class="up">상향</span>'
            goal_1 = f'<span class="up">{r["goal_1"]}</span>'

        elif goal_1 < goal_2:
            change_str = f'<span class="dn">하향</span>'
            goal_1 = f'<span class="dn">{r["goal_1"]}</span>'
        else:
            change_str = f"<span>유지</span>"
            goal_1 = f'<span>{r["goal_1"]}</span>'
        date_str = r["deal_date"]
        date_str = f"{int(date_str[4:6])}/{date_str[6:8]}"

        html += f"""
            <tr>
                <td>
                    <span>{r["stock_firm"]}</span>
                </td>
                <td>
                    <a href="#" class="obj">{r["title"]}</a>
                </td>
                <td class="text-right">
                    <span>{goal_1}</span>
                </td>
                <td class="text-center">
                    <span>{change_str}</span>
                </td>
                <td class="text-center">
                    <span>{date_str}</span>
                </td>
            </tr>
        """
    return html
