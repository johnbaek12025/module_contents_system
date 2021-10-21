def get_html(data):
    html = f"""
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
    # {'stkname': '펄어비스', 'ratio': 1.95, 'header': '소프트웨어게임 개발 및 퍼블리싱 업체'},
    # {'stkname': '골프존', 'ratio': -0.44, 'header': '골프시뮬레이터 개발 및 제조 전문기업'}
    html = ""
    for r in rows:
        html += f"""
            <tr>
                <td class="text-center">
                    <span>{r["stkname"]}</span>
                </td>
                <td class="text-right">
                    <span> {r["ratio"]}%</span>
                </td>
                <td>
                    <a href="#" class ="obj">{r["header"]}</a>
                </td>
            </tr>
        """
    return html
