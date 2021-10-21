def get_html(data):
    html = f"""
        <div class="module-tbl-txt">
            <span>주요 종목 동향</span>
        </div>
        <!-- //txt -->

    
        <table class="table module-table">
            <colgroup>    

                <col width="15%">
                <col width="15%">
                <col width="*%">
            </colgroup>
            <thead>
                <tr>
                    <th scope="col">종목명</th>
                    <th scope="col">등락률(*)</th>
                    <th scope="col">기업개요</th>
                </tr>
            </thead>
            <tbody>        
                {data}
            </tbody>
        </table>
        <!-- //tbl -->
        <div class="module-tbl-txt mt-10">
        <span class ="pull-left">※ 등락률은 1/25 10:23 기준입니다.</span>    
        </div>
        """
    return html


def get_row_html(rows):
    html = ""
    for r in rows:
        ratio = r["ratio"]

        if r["ratio"] == "-":
            ratio_str = "-"
        else:
            ratio_str = str(ratio) + "%"

        html += f"""
            <tr>
                <td class="text-center">
                    <a href="#" class ="obj">{r["stkname"]}</a>
                </td>
                <td class="text-center">
                    <span>{ratio_str}</span>
                </td>

                <td>
                    <span>{r["header"]}</span>
                </td>


            </tr>
        """
    return html