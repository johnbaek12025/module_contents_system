def get_html(data):
    html = f"""
        <table class="table module-table">
            <colgroup>    

                <col width="25%">
                <col width="*">
                <col width="12%">
                <col width="12%">
                <col width="12%">
            </colgroup>
            <thead>
                <tr>
                    <th scope="col">종목명</th>
                    <th scope="col">최근이슈</th>
                    <th scope="col">관련뉴스</th>
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
        date_str = r["datedeal"]
        date_str = f"{int(date_str[4:6])}/{date_str[6:8]}"

        title = r["title"]

        html += f"""
            <tr>
                <td>
                    <span>{r["stkcode"]}</span>
                </td>
                <td>
                    <a href ="#" class = "obj"> ({date_str}) {title}</a>
                </td>
                <td class="text-right">
                    <span>({r["cnt"]}건)</span>
                </td>
            </tr>
        """
    return html
