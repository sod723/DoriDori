"use strict"
let latitude = 0;
let longitude = 0;
var leaf_map;
var start_markers;
var end_markers;
var short_line;
var safe_line;
var start_x;
var start_y;
var resultArray = []; //출발지, 목적지 좌표

let code = '';

$(document).ready(function () {
    $('.route-wrap').hide()
    getLocation().then(location => {
        latitude = location['latitude']
        longitude = location['longitude'];
    }).then((arg) => {
        leaf_map = L.map('map').setView([latitude, longitude], 15)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18}).addTo(leaf_map);    //tileLayer의 {s}는 서버 도메인 , {z},{x},{y}는 타일 지도의 위치, addTo 매소드로 map에 타일 지도를 추가
        L.control.locate({
            position: 'topleft',
            strings: {
                title: "Show me where I am, yo!"
            }
        }).addTo(leaf_map);


    });
})

//클릭 마커 찍기
function getmarker() {
    leaf_map.addEventListener('click', function (e) {
        console.log(e.latlng.lat, e.latlng.lng);
        L.marker([e.latlng.lat, e.latlng.lng]).addTo(leaf_map);
    })
    $('#StartAddr').text(e.latlng.lat + ' ' + e.latlng.lng);
    $('#StartAddr').disabled();
}

// 현재의 위치 정보를 가져온다.
function getLocation() {
    return new Promise(resolve => {
        navigator.geolocation.watchPosition(function (position) {
            return resolve({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
            });
        });
    });
}

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
            code = '';
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
            code += data.sigunguCode;
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
            code += data.sigunguCode;
            //set value 도로명 주소
            document.getElementById("EndAddr").value = roadAddr;
        }
    }).open();
};


// //길찾기 버튼 클릭
$("#find_botton").click(function () {
    shortestRoute = []    //초기화
    safeRoute = []


    console.log(code);


    //출발지 목적지 주소 -> 좌표변환
    new Promise((succ, fail) => {
        $.ajax({
            type: 'POST',
            url: "/getspotpoint",

            data: {
                'StartAddr': $('#StartAddr').val(),
                'EndAddr': $('#EndAddr').val(),
                'code' : code,
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
        if(!resultArray['startaddr']){
            window.location.href = resultArray;
            return;
        }

        console.log(resultArray);
        console.log('좌표변환후 최단거리 실행');
    });


});
