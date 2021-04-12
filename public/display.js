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
return d > 1000 ? '#800026' :
	   d > 500  ? '#BD0026' :
	   d > 200  ? '#E31A1C' :
	   d > 100  ? '#FC4E2A' :
	   d > 50   ? '#FD8D3C' :
	   d > 20   ? '#FEB24C' :
	   d > 10   ? '#FED976' :
				  '#FFEDA0';
}

/** styling function for our GeoJSON layer so that its fillColor depends on our covid cases database **/
function style(feature) {
return {
	fillColor: getColor(feature.properties.density),
	weight: 2,
	opacity: 1,
	color: 'white',
	dashArray: '3',
	fillOpacity: 0.7
};
}

/** L.geoJson(statesData, {style: style}).addTo(map); **/

fetch('/counties',
{"method": "POST", 'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'}, "body" : JSON.stringify({})}
).then(res => res.json()).then(data => {
	for(var key in data){
		
	}
}

// load every prison
fetch('/date',
{"method": "POST", 'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'}, "body" : JSON.stringify({})}
).then(res => res.json()).then(data => {
	for(var key in data){
		var lva = data[key]
		if(lva.Latitude != "NA" && Number(lva.Cases) > 0){
			var mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
					color: '#0033FF',
				fillOpacity: 0.5,
				radius: 500
			}).addTo(mymap).bindPopup(Number(lva.Cases).toString() + ' Cases');

			if(lva.Cases != "NA"){
				mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
					color: getColor(lva.Cases),
					fillOpacity: 0.5,
					radius: 500
				}).addTo(mymap).bindPopup(Number(lva.Cases).toString() + ' Cases');
			}
			/**
			var myIcon = L.icon({
				iconUrl: "public/icon1.png"
			});

			if(Number(lva.Cases) > 1000){
				myIcon = L.icon({
					iconUrl: "public/icon2.png"
				});

			}
			**/
			/**var marker = L.marker([Number(lva.Latitude), Number(lva.Longitude)], {icon: myIcon}).addTo(mymap); **/
		}
	}
});
