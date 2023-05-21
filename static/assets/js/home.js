
"use strict"


var resultArray = []; //출발지, 목적지 좌표


var startcode;
var endcode;
let code = '';

//csrf token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

var shortestRoute = [];   //최단거리 좌표 정보
var safeRoute = [];

var input = document.getElementById("StartAddr");
input.onclick = function () {
    new daum.Postcode({
        oncomplete: function (data) {
            // 팝업에서 검색결과 항목을 클릭했을때 실행할 코드를 작성하는 부분입니다.

            // 도로명 주소의 노출 규칙에 따라 주소를 표시한다.
            // 내려오는 변수가 값이 없는 경우엔 공백('')값을 가지므로, 이를 참고하여 분기 한다.
            var roadAddr = data.roadAddress; // 도로명 주소 변수
            var extraRoadAddr = ''; // 참고 항목 변수

            // 법정동명이 있을 경우 추가한다. (법정리는 제외)
            // 법정동의 경우 마지막 문자가 "동/로/가"로 끝난다.
            if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
                extraRoadAddr += data.bname;
            }
            // 건물명이 있고, 공동주택일 경우 추가한다.
            if (data.buildingName !== '' && data.apartment === 'Y') {
                extraRoadAddr += (extraRoadAddr !== '' ? ', ' + data.buildingName : data.buildingName);
            }
            // 표시할 참고항목이 있을 경우, 괄호까지 추가한 최종 문자열을 만든다.
            if (extraRoadAddr !== '') {
                extraRoadAddr = ' (' + extraRoadAddr + ')';
            }
            startcode = data.sigunguCode;
            // 우편번호와 주소 정보를 해당 필드에 넣는다.
            // document.getElementById('sample4_postcode').value = data.zonecode;
            // document.getElementById("sample4_roadAddress").value = roadAddr;
            // document.getElementById("sample4_jibunAddress").value = data.jibunAddress;
            document.getElementById("StartAddr").value = roadAddr;
            //console.log(document.getElementById("StartAddr").value);
        }
    }).open();
};


var output = document.getElementById("EndAddr");
output.onclick = function () {
    new daum.Postcode({
        oncomplete: function (data) {
            var roadAddr = data.roadAddress; // 도로명 주소 변수
            var extraRoadAddr = ''; // 참고 항목 변수

            if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
                extraRoadAddr += data.bname;
            }
            if (data.buildingName !== '' && data.apartment === 'Y') {
                extraRoadAddr += (extraRoadAddr !== '' ? ', ' + data.buildingName : data.buildingName);
            }
            if (extraRoadAddr !== '') {
                extraRoadAddr = ' (' + extraRoadAddr + ')';
            }
            endcode = data.sigunguCode;
            //set value 도로명 주소
            document.getElementById("EndAddr").value = roadAddr;
        }
    }).open();
};


// //길찾기 버튼 클릭
$("#find_botton").click(function () {
    shortestRoute = []    //초기화
    safeRoute = []

    code = startcode + endcode;
    console.log(code);


    //출발지 목적지 주소 -> 좌표변환
    new Promise((succ, fail) => {
        $.ajax({
            type: 'POST',
            url: setpointpage,

            data: {
                'StartAddr': $('#StartAddr').val(),
                'EndAddr': $('#EndAddr').val(),
                'code': code,
                'csrfmiddlewaretoken': csrftoken,
            },

            success: (result) => {
                resultArray = result;
                console.log(resultArray);
                succ(result);  //성공하면 검색결과 처리
            },
            fail: (error) => {
                console.log(error);
                fail(error);
            }
        });
        //resultArray : startaddr, endaddr 좌표
    }).then((arg) => {
        // 로그인 안되어있을 시 로그인 창으로 이동
        if (!resultArray['startaddr']) {
            window.location.href = resultArray;
            return;
        }

        console.log(resultArray);
        console.log('좌표변환후 최단거리 실행');
        alert('위치가 저장되었습니다.');
        // $.ajax({
        //     type: "POST",
        //     url: "https://apis.openapi.sk.com/tmap/routes?version=1&format=json&callback=result",
        //     data: {
        //         "appKey": "l7xxa21398bdba4947eba835e6c00ec9ffaf",
        //         "startX": resultArray['startaddr'][1],
        //         "startY": resultArray['startaddr'][0],
        //         "endX": resultArray['endaddr'][1],
        //         "endY": resultArray['endaddr'][0],
        //         "reqCoordType": "WGS84GEO",
        //         "resCoordType": "EPSG3857",
        //         "startName": "출발지",
        //         "endName": "도착지"
        //     },
        //     success: (result) => {
        //         var resultData = result.features;       //출발지부터 목적지까지 경로좌표들(Point, Line)
        //         //결과 출력
        //         var tDistance = "총 거리 : " + ((resultData[0].properties.totalDistance) / 1000).toFixed(1) + "km";
        //         var tTime = " 총 시간 : " + ((resultData[0].properties.totalTime) / 60).toFixed(0) + "분";
        //         console.log(tDistance + " " + tTime);
        //         console.log((resultArray['startaddr'][1]));

        //         $('#short-route').text(tDistance)
        //         $('#short-time').text(tTime)

        //         for (var i in resultData) { //for문 [S]
        //             var geometry = resultData[i].geometry;  //좌표정보 ()

        //             if (geometry.type == "LineString") {

        //                 for (var j in geometry.coordinates) {
        //                     // 경로들의 결과값(구간)들을 포인트 객체로 변환
        //                     var latlng = new Tmapv2.Point(geometry.coordinates[j][0], geometry.coordinates[j][1]);

        //                     // 포인트 객체를 받아 좌표값으로 변환
        //                     var convertPoint = new Tmapv2.Projection.convertEPSG3857ToWGS84GEO(latlng);
        //                     // 포인트객체의 정보로 좌표값 변환 객체로 저장
        //                     var convertChange = new Tmapv2.LatLng(convertPoint._lat, convertPoint._lng);
        //                     // 배열에 담기
        //                     shortestRoute.push([convertChange['_lat'], convertChange['_lng']]);
        //                 }
        //             }
        //         }
        //         console.log('최단경로', shortestRoute);
        //     },
        //     fail: (error) => {
        //         console.log(error);
        //     }
        // });
    });
});