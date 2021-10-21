def get_html(rows, info):
    html = f"""
            <div class="module-tbl-txt">
                    <strong class="title">{rows['title']}</strong>
                </div>
                <!-- //guide -->

                <div class="module-txt-box">
                    {rows['description']}
                </div>
                <!-- //box -->

                <div class="module-tbl-txt mt-10">
                    {info[0]}
                    {info[1]}
            </div>
            """
    return html