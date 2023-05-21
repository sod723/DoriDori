"use strict"

let visible = true;

function startFatch() {
  if (app.getUserId() === 'None') return;
    
  const loader = document.querySelector('.preload');
  const emoji = loader.querySelector('.emoji');

  loader.style.display = "block";
  console.log(loader);

  const emojis = ["🕐", "🕜", "🕑", "🕝", "🕒", "🕞", "🕓", "🕟", "🕔", "🕠", "🕕", "🕡", "🕖", "🕢", "🕗", "🕣", "🕘", "🕤", "🕙", "🕥", "🕚", "🕦", "🕛", "🕧"];

  /* setInterval은 비동기 함수이기 때문에 then안에서 실행하게 되면 현재 프로미스의 실행 컨텍스트가 완료 될 때 까지
     동작하지 않게됨. 따라서 프로미스 이전에 미리 실행을 시켜야 한다.
  */
  const loadEmojis = (arr) => {
    let inter = setInterval(() => {
      if (visible) {
        emoji.innerText = arr[Math.floor(Math.random() * arr.length)];
      } else {
        clearInterval(inter);
        document.querySelector('.preload').style.display = "none";
      }
      //console.log(Math.floor(Math.random() * arr.length))
    }, 500);
  }

  const init = () => {
    loadEmojis(emojis);
  }
  init();

  let btns = document.querySelectorAll(".btn");

  btns.forEach((btn) => {
    btn.disabled = true;
  });
}

function fetchEnd() {
  if (app.getUserId() === 'None') return;

  visible = false;
};

// 전역변수 감추기
function init() {
  let map;
  let resultMarkerArr = [];
  let drawInfoArr = [];
  let resultdrawArr = [];
  let userId = document.body.dataset.userid;

  try {
    map = new Tmapv2.Map("map_div", {
      center: new Tmapv2.LatLng(37.49241689559544, 127.03171389453507),
      width: "100%",
      height: "80vh",
      zoom: 11,
      zoomControl: true,
      scrollwheel: true
    });
  
  } catch (error) {
    console.error("지도 띄우기", error);
  }

  function getMap() {
    return map;
  }

  function getResultMarkerArr() {
    return resultMarkerArr;
  }

  function getDrawInfoArr() {
    return drawInfoArr;
  }

  function getResultdrawArr() {
    return resultdrawArr;
  }

  function getUserId() {
    return userId;
  }

  function resettingMap() {

    if (resultMarkerArr.length > 0) {
      for (var i = 0; i < resultMarkerArr.length; i++) {
        resultMarkerArr[i].setMap(null);
      }
    }

    if (resultdrawArr.length > 0) {
      for (var i = 0; i < resultdrawArr.length; i++) {
        resultdrawArr[i].setMap(null);
      }
    }

    drawInfoArr = [];
    resultMarkerArr = [];
    resultdrawArr = [];
  }

  return {
    getMap: getMap,
    getResultMarkerArr: getResultMarkerArr,
    getDrawInfoArr: getDrawInfoArr,
    getResultdrawArr: getResultdrawArr,
    getUserId: getUserId,
    resettingMap: resettingMap
  }
}

/**
 * 매개변수를 바탕으로 지도를 업데이트하는 함수
 * @param {Array} path 좌표배열 
 * @param {Array} markers 마커좌표배열
 * @param {Array} points 지도영역위치
 */
function updateMap(path, markers, points) {
  drawRoute(path, "#229c9e");
  setMarker(markers);
  setMapBound(points);
}

/** 
 * 마커 찍기 함수 
 * @param {Array} points 좌표
*/
function setMarker(points) {
  let marker;
  const map = app.getMap();
  const resultMarkerArr = app.getResultMarkerArr();

  const busImg = "/MjAyMzAxMjVfMTAw/MDAxNjc0NjIwODkyNzIy.SbGS928H7yvR9ZRNvP_rqBJ2jiq_5IxnbvuKko7ckwkg.iddwW-EceWi528-cd2NgGlcTkqW_jqzNrUVNPFNKWKUg.PNG.keyhyun0123/image2vector.png?type=w580"
  const pinImg = "/MjAyMzAxMjVfNTcg/MDAxNjc0NjIzOTY3MTIz.bRdv0u15hKD0owBPoLETrLPlY8pfYC2t7pYNxMD0w5Mg.xSn1p05CUqANRlrzZBFc4QQiKrnMmxioIM0YdOt9_A8g.PNG.keyhyun0123/SE-72ea39b2-4a0d-4f7e-bae2-bb5a18a7c002.png?type=w580"

  points.forEach((point, idx) => {
    let iconImgURL = "https://postfiles.pstatic.net"

    if (idx == 0 || idx == points.length - 1) { //출발지, 도착지
      iconImgURL += pinImg;
    }
    else {
      iconImgURL += busImg
    }

    marker = new Tmapv2.Marker({
      position: new Tmapv2.LatLng(
        point.lat,
        point.lon),
      icon: iconImgURL,
      iconSize: new Tmapv2.Size(35, 35),
      title: point.name,
      map: map
    });

    resultMarkerArr.push(marker);
  });
}

/**
 * 경로를 전달한 색상으로 지도에 표시
 * @param {Array} path 경로
 * @param {string} color 색상
 */
function drawRoute(path, color) {
  let drawInfoArr = [];
  let routeLine;
  const map = app.getMap();
  const resultdrawArr = app.getResultdrawArr();

  path.forEach((coordinate) => {
    let latLng = new Tmapv2.LatLng(coordinate[1], coordinate[0]);
    drawInfoArr.push(latLng);
  });

  routeLine = new Tmapv2.Polyline({
    path: drawInfoArr,
    strokeColor: color,
    strokeWeight: 4,
    map: map
  });

  resultdrawArr.push(routeLine);
}

/** 
 * 지도의 범위를 매개변수로 전달된 GPS들을 기준으로 변경하는 함수
 * @param {Array} points GPS정보배열 
*/
function setMapBound(points) {

  let maxLatLon = { 'lat': 0, 'lon': 0 };
  let minLatLon = { 'lat': 50, 'lon': 150 };

  let centerLat;
  let centerLon;

  let boundX;
  let boundY;

  const map = app.getMap();

  points.forEach((poi) => {
    if (maxLatLon.lat < poi.lat) {
      maxLatLon.lat = poi.lat;
    }
    if (maxLatLon.lon < poi.lon) {
      maxLatLon.lon = poi.lon;
    }
    if (minLatLon.lat > poi.lat) {
      minLatLon.lat = poi.lat;
    }
    if (minLatLon.lon > poi.lon) {
      minLatLon.lon = poi.lon;
    }
  });

  console.log(maxLatLon, minLatLon);
  centerLat = (maxLatLon.lat + minLatLon.lat) / 2.0;
  centerLon = (maxLatLon.lon + minLatLon.lon) / 2.0;

  boundX = (maxLatLon.lat - minLatLon.lat) / 2.0;
  boundY = (maxLatLon.lon - minLatLon.lon) / 2.0;

  let bounds = new Tmapv2.LatLngBounds();

  bounds.extend(new Tmapv2.LatLng(centerLat + boundX, centerLon));
  bounds.extend(new Tmapv2.LatLng(centerLat - boundX, centerLon));
  bounds.extend(new Tmapv2.LatLng(centerLat, centerLon + boundY));
  bounds.extend(new Tmapv2.LatLng(centerLat, centerLon - boundY));

  map.fitBounds(bounds, 70);
}

/**
 * 경로의 정보(시간, 거리, 명칭)을 담고 있는 li 생성
 * @param {Array} pointArray 
 * @param {Array} timeArray 
 * @param {Array} distanceArray
 */
function createRouteInfoWindow(pointArray, timeArray, distanceArray) {
  let route_container = document.querySelector("#route_list");
  const map = app.getMap();
  // 기존 인터페이스 초기화
  if (route_container.childNodes) {
    route_container.innerHTML = '';
  }

  //forEach로 바꾸기
  for (let i = 0; i < pointArray.length; i++) {
    let route = document.createElement('li');
    let textDiv = document.createElement('div');

    route.setAttribute('class', 'route');
    route.dataset.lat = pointArray[i].lat;
    route.dataset.lon = pointArray[i].lon;

    textDiv.innerHTML = pointArray[i].name;
    route.appendChild(textDiv);

    if (i < pointArray.length - 1) {
      let time, distance;
      let childDiv = document.createElement('div');

      time = secToHHMMString(timeArray[i]);
      distance = mToKmString(distanceArray[i]);
      childDiv.innerHTML = time + " ↓ " + distance;

      route.appendChild(childDiv);
    } else {
      let totalTime = secToHHMMString(timeArray.reduce((a, b) => a + b, 0));
      let totalDistance = mToKmString(distanceArray.reduce((a, b) => a + b, 0));
      let totalTextNode = document.createTextNode("총 시간: " + totalTime + ", 총 거리: " + totalDistance);

      route_container.parentNode.appendChild(totalTextNode);
    }

    route.addEventListener('click', (event) => {
      let coord = new Tmapv2.LatLng(route.dataset.lat, route.dataset.lon);
      map.setCenter(coord);
      map.setZoom(15);
    });

    route_container.appendChild(route);
  }
}

function createSetBoundButton(boundPoints) {
  const buttonCon = document.querySelector("#bound_button");
  let button = document.createElement('button');
  button.addEventListener('click', () => {
    setMapBound(boundPoints);
  });
  button.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>';
  buttonCon.appendChild(button);
}


/**
 * 인자로 전달된 초 단위의 시간을 분, 시간 단위로 변환한 문자열을 반환하는 함수
 * @param {number} sec 초
 * @returns {string} 분/시간 단위 문자열
*/
function secToHHMMString(sec) {
  let dateString = new Date(sec * 1000).toISOString().slice(11, 16);
  let hour = dateString.slice(0, 2);
  let min = dateString.slice(3);
  let timeString;

  if (min[0] == '0') {
    min = min[1];
  }

  if (hour == '00') {
    timeString = min + "분";
  } else {
    timeString = hour.slice(1) + "시간 " + min + "분";
  }

  return timeString;
}

/**
 * 인자로 전달된 미터 단위의 거리를 미터, 키로미터 다위로 변환한 문자열을 반환하는 함수
 * @param {number} m m단위 거리
 * @returns {string} m/km 단위 문자열
*/
function mToKmString(m) {
  let km = m / 1000;
  let distanceString;
  if (km > 1) {
    distanceString = km.toFixed(1) + " km";
  } else {
    distanceString = m + " m";
  }

  return distanceString;
}

const app = init();

export const Map = {
  state: app,
  startFatch: startFatch,
  fetchEnd, fetchEnd,
  updateMap: updateMap,
  setMarker: setMarker,
  drawRoute: drawRoute,
  setMapBound: setMapBound,
  createRouteInfoWindow: createRouteInfoWindow,
  createSetBoundButton: createSetBoundButton,
}