# Team DoriDori


<p align="center"><img src="./static/assets/img/favicon.png"></p>

> 광운대학교 SW산학연계 5인 팀프로젝트<br>
> 개발 기간: 2022.12.15~2023.1.30

## 프로젝트 소개
광운대학교 산학연계 SW프로젝트는 사업체(기업)에서 제안한 주제를 학생(팀)이 선정하여 주제에 대한 SW프로젝트를 진행하는 프로그램입니다. 저희 팀은 위치정보에 관한 집계 자동화 시스템 개발이라는 주제를 선택하여 사용자의 위치정보 군집화를 통한 셔틀버스 노선편성 서비스를 개발하였습니다.<br>

해당 프로젝트는 매일 아침 힘겨운 출근길을 편안하게 만들어 주는 것에 도움을 주기 위해 개발되었습니다. 지도 서비스는 T Map API를 사용했습니다.

## 기술스택
### Framework
<img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white"><br>

### Development
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white">  <img src="https://img.shields.io/badge/bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white"><br>

### Datebase

 <img src="https://img.shields.io/badge/sqlite-6DB33F?style=for-the-badge&logo=sqlite&logoColor=white">

## 결과예시
![스크린샷 2023-01-27 오후 8 51 30](https://user-images.githubusercontent.com/81648520/215080342-fc085832-66c0-4893-94ee-2962f66e0f67.png)

[구현 부분 영상](https://youtu.be/2uMvvIf_i0A)

## 주요 기능
### :star: 사용자의 출발지와 목적지 저장
- 위치저장 버튼을 누르면 사용자의 위처정보를 데이터 베이스에 저장
### :star: 출발지와 목적지의 버스 경로 지도에 표시
- 길찾기 버튼을 눌렀을 때 같은 행정동 사용자들의 위치정보를 클러스터링하여 새로운 출근길 노선 표시
- 사용자가 이용할 경로를 지도에 표시
- 출발지에서 탑승지, 하차지에서 목적지는 도보 경로, 탑승지에서 하차지까지는 버스의 경로를 나타냄

## 문제 상황
- 웹 애플리케이션이 1GB의 지나친 메모리를 사용하여 성능이 떨어짐

- 지도에 경로를 표시할 때 GPS 좌표의 배열을 포함하는 경로 인스턴스를 생성해야 함

- 경로 인스턴스가 좌표 배열이 아닌 좌표 하나만 담는 상태로 만들어져 선을 그리는 것이 아니라 점을 찍어 선을 그리는 형태로 구현된 것을 발견함.

- 함수에 전달될 인자가 GPS좌표들을 담는 배열로 전달되도록 자료구조의 형태를 통일하고 알고리즘을 다시 설계하고 구현
  - 도보를 표시하기 위한 좌표 배열의 경우 `출발지-탑승지`, `하차지-목적지`로 두 개의 경로 배열을 담는 자료구조로 표현<br>
  ```js
  [
    [[출발지 위도, 출발지 경도] ... [탑승지 위도, 탑승지 경도]],
    [[하차지 위도, 하차지 경도] ... [목적지 위도, 목적지 경도]]
  ]
  ```
  - 버스의 경로는 `탑승지-하차지`로 하나의 경로 배열을 담는 자료구조로 표현<br>
  ```
  [
    [탑승지 위도, 탑승지 경도] ... [하차지 위도, 하차지 경도]
  ]
  ```
  - 경로를 그리는 함수 `drawRoute`는 매개변수로 GPS 경로를 담는 배열을 받아 경로 인스턴스를 생성함
    - 도보의 경로는 `forEach`문을 사용해 경로 인스턴스를 `출발지-탑승지`, `하차지-목적지` 경로로 2개 생성하고, 버스의 경로는 `탑승지-하차지`로 하나의 경로 인스턴스를 생성함
- 결과 적게는 800개에서 많게는 1600개의 인스턴스가 생성되어 소모되던 1GB의 메모리가 10MB로 감소하여 애플리케이션의 성능이 향상됨

## 디렉토리 구조

```
├ manage.py
├ README.md
├ requirements.txt
├ DoriDori
│ ├─ asgi.py
│ ├─ settings.py
│ ├─ urls.py
│ ├─ views.py
│ ├─ wsgi.py
│ └─ __init__.py
├ board : 버스 입찰페이지 관리
│ ├─ admin.py
│ ├─ apps.py
│ ├─ forms.py
│ ├─ migrations
│ │  ├─ 0001_initial.py
│ │  └─ __init__.py
│ ├─ models.py
│ ├─ templatetags
│ │  └─ board_filter.py
│ ├─ tests.py
│ ├─ urls.py
│ ├─ views
│ │  ├─ answer_views.py
│ │  ├─ base_views.py
│ │  └─ question_views.py
│ └─ __init__.py
├ content : 지도 페이지 관리
│ ├─ admin.py
│ ├─ apps.py
│ ├─ migrations
│ ├─ models.py
│ ├─ tests.py
│ ├─ urls.py
│ ├─ views.py
│ └─ __init__.py
├ static
│ ├─ assets
│ │  ├─ css
│ │  ├─ img
│ │  ├─ js
│ │  │  ├─ home.js
│ │  │  ├─ main.js
│ │  │  ├─ map.mjs : map.js 모듈
| |  |  ├─ map.js : 지도 페이지 js파일
│ │  │  └─ Readme.txt
│ │  ├─ scss
│ │  |
│ │  └─ vendor
│ └─ forms
├ templates : html파일
│ ├─ base.html
│ ├─ board
│ │  ├─ answer_form.html
│ │  ├─ question_detail.html
│ │  ├─ question_form.html
│ │  └─ question_list.html
│ ├─ footer.html
│ ├─ form_errors.html
│ ├─ home.html
│ ├─ map.html
│ ├─ navbar.html
│ └─ user
│    ├─ join.html
│    ├─ login.html
│    └─ signup.html
└ user: 사용자 정보 관리
 ├─ admin.py
 ├─ apps.py
 ├─ forms.py
 ├─ migrations
 │  └─ __init__.py
 ├─ models.py
 ├─ tests.py
 ├─ urls.py
 ├─ views.py
 └─ __init__.py
```
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

# no such table 에러가 발생할 경우 
  
  python manage.py migrate --run-syncdb 
  
  명령어를 실행하고 다시 서버를 실행해 주십시오.

```
