var mymap = L.map('mapid').setView([37.125286284966805, -120.0146484375], 6);

L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiNDQ3dGVhbTEwIiwiYSI6ImNrbjQyZTR5ZzFuanAydmxudDBsdG5qeHQifQ.ZRPB_88o-9nBmNgmKBw50Q', {
	maxZoom: 18,
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
		'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1
}).addTo(mymap);

/** onClick Listener, zooms in on map when user clicks on location**/
function onMapClick(e) {
		 mymap.zoomIn();
}
mymap.on('click', onMapClick);

/** Color Settings that will coordinate with Covid Cases Density **/
function getColor(d) {
return d > 2000 ? '#800026' :
	   d > 1000  ? '#BD0026' :
	   d > 500  ? '#E31A1C' :
	   d > 200  ? '#FC4E2A' :
	   d > 100   ? '#FD8D3C' :
	   d > 50   ? '#FEB24C' :
	   d > 25   ? '#FED976' :
				  '#FFEDA0';
}

/** styling function for our GeoJSON layer so that its fillColor depends on our covid cases database **/

counties_cases = {};

function style(feature) {
	console.log(feature);
	console.log(feature.properties.name);
return {
	fillColor: getColor(counties_cases[feature.properties.name]),
	weight: 2,
	opacity: 1,
	color: 'white',
	dashArray: '3',
	fillOpacity: 0.7
};
}

/** L.geoJson(statesData, {style: style}).addTo(map); **/

var countyMarkers = {};
function renderCounties(data) {
	for(var key in data){
		if(countyMarkers[key] == null){
			geojsonFile = data[key][0];
			console.log(geojsonFile);
			console.log(geojsonFile.properties);
			// geojsonFile.properties.density = data[key][1]
			counties_cases[key] = data[key][1].Cases;
			console.log(data[key][1]);
			var mypoly = L.geoJSON(geojsonFile, {style: style}).addTo(mymap);
			countyMarkers[key] = mypoly;
		} else {
			counties_cases[key] = data[key][1].Cases;
			console.log(data[key][1]);
			countyMarkers[key].setStyle({fillColor: getColor(counties_cases[key])});
		}
	}
}

var facilityMarkers = {};
var facilityCases = {};
function renderFacilities(data) {
	for(var key in facilityMarkers){
		facilityMarkers[key].setStyle({color: getColor(0)});
	}
	for(var key in data){
		if(facilityMarkers[key] == null){
			var lva = data[key]
			if(lva.Latitude != "NA" && Number(lva.Cases) > 0){
				var mycircle;
				if(lva.Cases != "NA"){
					facilityCases[key] = lva.Cases;
					mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
						color: getColor(lva.Cases),
						fillOpacity: 0.5,
						radius: 5000
					}).addTo(mymap).bindPopup(Number(facilityCases[key]).toString() + ' Cases');
				} else {
					mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
						color: '#0033FF',
						fillOpacity: 0.5,
						radius: 5000
					}).addTo(mymap).bindPopup(Number(facilityCases[key]).toString() + ' Cases');
				}
				console.log("Created", mycircle);
				facilityMarkers[key] = mycircle;
			}
		} else {
			var lva = data[key]
			if(lva.Latitude != "NA" && Number(lva.Cases) > 0){
				facilityMarkers[key].setStyle({color: getColor(lva.Cases)});
				facilityCases[key] = lva.Cases;
				facilityMarkers[key].setPopupContent(Number(facilityCases[key]).toString() + ' Cases');
				console.log(lva.Cases)
				console.log(key);
			} else {
				facilityCases[key] = 0;
				facilityMarkers[key].setPopupContent(Number(facilityCases[key]).toString() + ' Cases');
			}
		}
	}
}

function load_on_date(date){
	var date_fragment = '';
	if(date){
		date_fragment = '?date=' + date
	}
	fetch('/counties' + date_fragment,
	{"method": "POST", 'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'}, "body" : JSON.stringify({})}
	).then(res => res.json()).then(renderCounties);

	// load every prison
	fetch('/data' + date_fragment,
	{"method": "POST", 'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'}, "body" : JSON.stringify({})}
	).then(res => res.json()).then(data =>
		{
			console.log("Received data.");
			renderFacilities(data.List);
			console.log("Received data.");
			console.log(data);
		}
	);
}

load_on_date(); // loads with the default date - i.e. today's date

const selectElement = document.querySelector('.mapdate');
function load_button_pressed(){
	console.log("Load button pressed.");
	load_on_date(selectElement.value)
}

selectElement.addEventListener('change', load_button_pressed);
