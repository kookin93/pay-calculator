급여계산기 Streamlit 앱
초보자용 복붙 가이드

0. 준비물
Windows 기준 설명입니다
Python 3.11 이상 설치가 필요합니다
설치할 때 Add Python to PATH 체크가 필요합니다

1. 새 폴더 만들기
예시
C:\pay_app

2. 아래 파일 2개를 같은 폴더에 저장
app.py
README.txt

3. 관리자 비밀번호 파일 만들기
아래 경로의 폴더를 새로 만듭니다
C:\pay_app\.streamlit

그 다음 아래 파일을 새로 만듭니다
C:\pay_app\.streamlit\secrets.toml

secrets.toml 내용은 아래를 그대로 복붙합니다
ADMIN_PASSWORD="원하는비밀번호"

예시
ADMIN_PASSWORD="inhwa1234"

4. PowerShell 실행
시작 메뉴에서 PowerShell 실행

5. 폴더 이동
cd C:\pay_app

6. 가상환경 만들기
python -m venv .venv

7. 가상환경 켜기
.venv\Scripts\activate

8. 필요한 패키지 설치
pip install -U streamlit pandas

9. 앱 실행
streamlit run app.py

10. 사용 방법
브라우저가 자동으로 열립니다
안 열리면 PowerShell에 표시되는 Local URL을 복사해서 브라우저에 붙여넣습니다

11. 최저시급을 관리자만 바꾸는 방법
오른쪽 또는 왼쪽 사이드바의 관리자 영역에서
관리자 비밀번호를 입력합니다
관리자 모드로 바뀝니다
최저시급 변경 값 입력 후 저장 버튼을 누릅니다

최저시급 값은 config.json에 저장됩니다
다음 실행에도 그대로 유지됩니다
일반 모드에서는 최저시급 숫자만 보이고 변경 입력창은 보이지 않습니다
