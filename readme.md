# module_contents_system
  1. 프로그램 설명
    
    - 해당 프로젝트는 분석DB에 이벤트가 발생시 모듈 콘텐츠 시스템에서 
      이벤트에 해당하는 모듈 실행하여 데이터를 가공하여
      가공 결과를 html화 하여 관련 db에 적재하는 프로그램 입니다.
           
  2. 프로젝트 구성도
      
      ![flow2](https://user-images.githubusercontent.com/62003412/139821513-5c7f7335-6164-4277-ac7d-91e361095ec5.PNG)

  3. tree
      ├─adm
      │  └─jobs
      │      ├─html
      │      └─workshop
      ├─bin
      ├─examples
      ├─fonts
      │  └─arial
      ├─html_test
      │  ├─css
      │  ├─img
      │  │  ├─header
      │  │  └─sub
      │  │      ├─board
      │  │      ├─bot
      │  │      ├─btn
      │  │      └─item
      │  │          └─rmd
      │  └─js
      └─tests
     
## ADM 실행 순서

1. git 설치
```
https://git-scm.com/
```

2. adm 프로그램 설치
```
git clone https://gitlab.com/tp.rc.cyg/analysis_data.git
```

3. Python 3.8 설치
```
https://www.python.org/downloads/
```

4. 라이브러리 설치
- 파이썬 라이브러리
```
pip install -r requirements.txt
```

- 오라클 라이브러리
아래 링크에서 다운로드 받아 설치
```
https://www.oracle.com/kr/database/technologies/instant-client/winx64-64-downloads.html
```

5. adm/examples 에 있는 adm.cfg 를 수정하여서 특정 폴더에 저장
```
Ex) adm/cfg/adm.cfg
```

6. Unit-test 를 실행하여 문제 없는지 확인 (테스트 작성을 안했기 때문에, 패스)
```
Ex) tox
Ex) python setup.py test
Ex) python setup.py test --test-suite tests.test_util.TestUtil
Ex) python setup.py test --test-suite tests.test_util.TestUtil.test_to_int

```

7. 실행
```
# 옵션 파일이 adm/cfg/에 위치할 경우
cd bin
python ad-manager.py --config=../cfg/cm.cfg
```
