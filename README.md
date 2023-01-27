# Team DoriDori

사용자 위치정보 군집화를 통한 셔틀버스 노선편성 서비스 입니다.

---

## 결과예시
![스크린샷 2023-01-27 오후 8 51 30](https://user-images.githubusercontent.com/81648520/215080342-fc085832-66c0-4893-94ee-2962f66e0f67.png)

## 실행

python 3.7 이상 버전 설치 후

```
- 가상환경 생성 
python -m venv venv

- 가상환경 실행
source ./venv/Scripts/activate

- 필요 package 설치
pip install -r requirements.txt

- migrate 명령어로 DB 생성
python manage.py makemigrations
python manage.py migrate

- 서버 실행
python manage.py runserver

- 브라우져로 접속
http://127.0.0.1:8000/
```

## 주의사항
```
# 같은 지역의 사용자가 4명 이상이 모였을 경우에만 클러스터링이 실행됩니다.
```
