"use strict"
import {Map} from './map.mjs'

const app = Map.state;

/** 길찾기 버튼 클릭 이벤트 
경로 그리기, 지도 업데이트
*/
const searchRouteButton = document.querySelector("#btn_select");
searchRouteButton.addEventListener('click', (event) => {
  app.resettingMap();
  
  let routeInfo;
  let busPath;
  let markers;

  let boundPoints;

  let routeInfoArr = [];

  if(document.body.dataset.userid !== "None"){
    Map.startFatch();
  }

  fetch("/getRoute")
    .then(response => response.text())
    .then((text) => {
      if(text === "None"){
        alert("경로를 만들기에 같은 행정동의 이용자 수가 부족합니다.")
        throw Error('인원 부족');
      }
      // 경로 그리기,마커 찍기, 지도 영역 설정

      try {
        routeInfo = JSON.parse(text);
        
        if (routeInfo.walking) {
          let busTime = routeInfo.bus.time.reduce((a, b) => a + b, 0);
          let busDistance = routeInfo.bus.distance.reduce((a, b) => a + b, 0);
  
          routeInfo.walking.time.splice(1, 0, busTime);
          routeInfo.walking.distance.splice(1, 0, busDistance);
  
          markers = JSON.parse(JSON.stringify(routeInfo.walking.points)); // 출발지-탑승지
          markers.splice(2, 0, ...routeInfo.bus.viaPoints); // 출발지 - 지나는 버스정류장 - 도착지
  
          let walkPath = routeInfo.walking.path;
          walkPath.forEach((path) => {
            Map.drawRoute(path, "#ff0000");
            // drawRoute(path, "#ff0000");
          })
  
          busPath = routeInfo.bus.path;
          boundPoints = routeInfo.walking.points;
  
          // point, time, distance
          routeInfoArr.push(routeInfo.walking.points);
          routeInfoArr.push(routeInfo.walking.time);
          routeInfoArr.push(routeInfo.walking.distance);
        }
        else {
          busPath = routeInfo.path;
          markers = routeInfo.viaPoints;
          boundPoints = routeInfo.viaPoints;
  
          routeInfoArr.push(routeInfo.viaPoints);
          routeInfoArr.push(routeInfo.time);
          routeInfoArr.push(routeInfo.distance);
        }
  
        // 중복제거
        // updateMap(busPath, markers, boundPoints);
        Map.updateMap(busPath, markers, boundPoints);
        return routeInfoArr
      } catch (e) {
        window.location.href = text;
        return undefined;
      }
    })
    .then((routeInfoArr) => {
      // 경로 인터페이스 생성
      if(routeInfoArr){
        Map.createRouteInfoWindow(routeInfoArr[0], routeInfoArr[1], routeInfoArr[2]);
        Map.createSetBoundButton(routeInfoArr[0]);

        // createRouteInfoWindow(routeInfoArr[0], routeInfoArr[1], routeInfoArr[2])
        // createSetBoundButton(routeInfoArr[0]);
        alert("경로가 검색되었습니다.");

      }
    })
    .catch(console.log) // JSON데이터가 아닌 경우
    .finally(Map.fetchEnd);
});

const { get, set } = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
const inputs = document.querySelectorAll(".form-control");

/** 
 * map input tag value 속성 getter와 setter 커스텀
 * input.value를 동적으로 변경하면 change event가 발생하지 않음
*/
inputs.forEach((input) => {
  Object.defineProperty(input, 'value', {
    get() {
      return get.call(this);
    },
    /**
     * 사용자가 주소 입력시 해당하는 위치에 마커를 표시하고 지도의 중심좌표 이동 
     * @param {string} newVal 도로명 주소
     */
    set(newVal) {

      const options = {
        method: 'GET',
        headers: { accept: 'application/json', appKey: 'l7xx0540ab9b13084d30b44950c8a1b7f405' }
      };
      fetch('https://apis.openapi.sk.com/tmap/geo/fullAddrGeo?addressFlag=F00&version=1&fullAddr=' + newVal, options)
        .then(response => response.json())
        .then(response => response.coordinateInfo)
        .then((resultInfo) => {
          
          if (resultInfo?.coordinate) {
            let map = app.getMap();
            let coordinateInfo = resultInfo.coordinate[0]
            let markerPosition = new Tmapv2.LatLng(Number(coordinateInfo.newLat), Number(coordinateInfo.newLon));

            // 마커 올리기
            let marker = new Tmapv2.Marker(
              {
                position: markerPosition,
                icon: "http://tmapapi.sktelecom.com/upload/tmap/marker/pin_b_m_a.png",
                iconSize: new Tmapv2.Size(
                  24, 38),
                map: map
              });
            map.setCenter(markerPosition);
            map.setZoom(18);
            app.getResultMarkerArr().push(marker);
          }
          else{
            alert('주소를 다시 입력해주세요.');
          }
        })
        .catch(err => console.error(err));

      // this -> input tag domelement
      return set.call(this, newVal);
    }
  });
})

// initTamp();