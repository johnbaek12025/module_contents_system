def add_html_frame(test, left):
    html = f"""
        <!DOCTYPE html>
        <html lang="ko">        ​
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>thinkpool</title>
            <!-- font -->
            <link rel="preconnect" href="https://fonts.gstatic.com">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;300;400;500;700;900&display=swap" rel="stylesheet">
            <!-- Latest compiled and minified CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
            <!-- Optional theme -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap-theme.min.css" integrity="sha384-6pzBo3FDv/PJ8r2KRkGHifhEocL+1X2rVCTTkUfGk7/0pbek5mMa1upzvWbrUbOZ" crossorigin="anonymous">
            <!-- basic css -->
            <link rel="stylesheet" href="css/common.css">
            <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
            <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
            <!--[if lt IE 9]>
                <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
                <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
                <![endif]-->
            <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
            <script src="https://code.jquery.com/jquery-1.12.4.min.js" integrity="sha384-nvAa0+6Qg9clwYCGGPpDQLVpLNn0fRaROjHqs13t4Ggj3Ez50XnGQqc/r8MhnRDZ" crossorigin="anonymous"></script>
            <!-- Latest compiled and minified JavaScript -->
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>
            <!-- bxslider -->
            <script src="https://cdn.jsdelivr.net/bxslider/4.2.12/jquery.bxslider.min.js"></script>
            <!-- basic js -->
            <script src="js/main.js"></script>
        </head>        ​
        <body> 
         <div id="wrap">
        <section id="container_w">
            <div id="container">

                <div id="content" class="sub nbg mt-20">
                    <!-- module 예시 1 -->

         <section class="module-section mt-40">
                        <h4 class="sr-only">모듈 네이밍</h4>

                        <div class="modulebox">
        <!-- // section 추가-->
            <div class="left">
                                <div class="module-content">
                                    <div class="title">
                                        <span>모듈제목</span>
                                    </div>
                                    <!-- //title -->
                                    <div class="title mt-20">
                                        {left}
                                        <!-- // colorClass =  up-red , dn-blue -->
                                    </div>
                                    <!-- //title -->
                                </div>
                                <!-- //content -->
                                <div class="module-content">
                                    <div class="text">
                                        <span>
                                            삼성전자에 대해 최근 5일동안 5개의 <br>
                                            증권사에서 목표가를 상향 조정함
                                        </span>
                                    </div>
                                    <!-- //text -->

                                    <div class="text-s mt-20">
                                        <span>10시 11분 기준</span>
                                    </div>
                                    <!-- //text -->
                                </div>
                                <!-- //content -->
                            </div>
                            <!-- //left -->
            <div class="right">
                <div class="module-content">
                    {test}
                </div>
            </div>
            <!--right-->             
            </div>
            <!--modulebox-->            
            </section>
            <!--sub nbg mt-20-->
             </div>             
             <!--id="content" class="sub nbg mt-20-->
            </div>
            <!--id="container"-->
            </section >
            <!--"container_w"-->
                <div>
                <!--"wrp"-->
        </body>
        </html>
    """
    return html


def save_to_file(file_name, data, left):
    html = add_html_frame(data, left)
    path = f"html_test/{file_name}.html"
    with open(path, "w") as f:
        f.write(html)
