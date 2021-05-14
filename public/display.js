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
function lerpColor(a, b, amount) {

    var ah = parseInt(a.replace(/#/g, ''), 16),
        ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
        bh = parseInt(b.replace(/#/g, ''), 16),
        br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
        rr = ar + amount * (br - ar),
        rg = ag + amount * (bg - ag),
        rb = ab + amount * (bb - ab);

    return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);
}

var dateColoringEnabled = false;
var caseDensity = false;

function getColor(d, dateDifference, totalPopulation) {

	if(totalPopulation != null){
		d = 2500 * d / totalPopulation;
	}

	var Value = d > 2000 ? '#800026' :
		   d > 1000  ? '#BD0026' :
		   d > 500  ? '#E31A1C' :
		   d > 200  ? '#FC4E2A' :
		   d > 100   ? '#FD8D3C' :
		   d > 50   ? '#FEB24C' :
		   d > 25   ? '#FED976' :
					  '#FFEDA0';
	if(dateDifference != null && dateColoringEnabled){
		if(dateDifference < 15) {
			Value = lerpColor(Value, "#aaaaaa", dateDifference / 15);
		} else {
			Value = "#aaaaaa";
		}
	}
	return Value
}

/** styling function for our GeoJSON layer so that its fillColor depends on our covid cases database **/

counties_cases = {};
counties_dates = {}

function style(feature) {
return {
	fillColor: getColor(counties_cases[feature.properties.name], DateDifference(counties_dates[feature.properties.name])),
	weight: 2,
	opacity: 1,
	color: 'white',
	dashArray: '3',
	fillOpacity: 0.7
};
}

/** L.geoJson(statesData, {style: style}).addTo(map); **/
var current_map_date;

function DateDifference(inputDate){
	var start = SQLDateToDate(inputDate).getTime(); // time in milliseconds
	var thisTime = SQLDateToDate(current_map_date).getTime();

	return (thisTime - start) / (1000 * 24 * 60 * 60);
}

var countyMarkers = {};
function renderCounties(data) {
	for(var key in countyMarkers){
		countyMarkers[key].setStyle({fillColor: getColor(0)});
	}
	for(var key in data){
		if(countyMarkers[key] == null){
			geojsonFile = data[key][0];
			// geojsonFile.properties.density = data[key][1]
			counties_cases[key] = data[key][1].Cases;
			counties_dates[key] = data[key][1].Date;
			var mypoly = L.geoJSON(geojsonFile, {style: style}).addTo(mymap);
			countyMarkers[key] = mypoly;
		} else {
			counties_cases[key] = data[key][1].Cases;
			counties_dates[key] = data[key][1].Date;
			countyMarkers[key].setStyle({fillColor: getColor(data[key][1].Cases, DateDifference(data[key][1].Date))});
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
					if(caseDensity){
						mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
							color: getColor(lva.Cases, DateDifference(lva.Date), lva.Population),
							fillOpacity: 0.5,
							radius: 5000
						}).addTo(mymap)
					} else {
						mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
							color: getColor(lva.Cases, DateDifference(lva.Date)),
							fillOpacity: 0.5,
							radius: 5000
						}).addTo(mymap)
					}
					mycircle.bindPopup(Number(facilityCases[key]).toString() + ' Cases ' + lva.Population.toString() + ' population');
					facilityCases[key] = lva.Cases;

				} else {
					mycircle = L.circle([Number(lva.Latitude), Number(lva.Longitude)], {
						color: '#0033FF',
						fillOpacity: 0.5,
						radius: 5000
					}).addTo(mymap).bindPopup(Number(facilityCases[key]).toString() + ' Cases');
				}
				facilityMarkers[key] = mycircle;
			}
		} else {
			var lva = data[key]
			if(lva.Latitude != "NA" && Number(lva.Cases) > 0){
				if(caseDensity){
					facilityMarkers[key].setStyle({color: getColor(lva.Cases, DateDifference(lva.Date), lva.Population)});
				} else {
					facilityMarkers[key].setStyle({color: getColor(lva.Cases, DateDifference(lva.Date))});
				}
				facilityCases[key] = lva.Cases;
				facilityMarkers[key].setPopupContent(Number(facilityCases[key]).toString() + ' Cases ' + lva.Population.toString() + ' population');
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
		current_map_date = date;
	} else {
		current_map_date = parseDate(new Date());
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
		}
	);
}

load_on_date(); // loads with the default date - i.e. today's date


function checkboxGreyer() {
	dateColoringEnabled = document.getElementById("dateColoringCheckbox").checked;
	load_on_date(current_map_date);
}

// This is to switch between case # and case density.
function checkboxDensity(){
	caseDensity = document.getElementById("densityColoringCheckbox").checked;
	load_on_date(current_map_date);
}

const selectElement = document.querySelector('.mapdate');
function load_button_pressed(){
	console.log("Load button pressed.");
	load_on_date(selectElement.value);
}

selectElement.addEventListener('change', load_button_pressed);

function SQLDateToDate(n) {
	var re = /(.+)\-(.+)\-(.+)/;
	var info = re.exec(n);
	console.log(info);
	var d = new Date(parseInt(info[1]), parseInt(info[2]) - 1, parseInt(info[3]), 0, 0, 0, 0);
	return d;
}

function parseDate(d) {
	var Year = d.getUTCFullYear();
	Year = String(Year).padStart(4, '0');
	var Month = (d.getUTCMonth() + 1);
	Month = String(Month).padStart(2, '0');
	var Day = d.getUTCDate();
	Day = String(Day).padStart(2, '0');
	var n = Year + "-" + Month + "-" + Day;
	return n;
}

var sliderStart = "2020-03-01"
var sliderEnd = "2021-05-10"

var scale = 100;
function slider(n) {
	var start = SQLDateToDate(sliderStart).getTime(); // time in milliseconds
	var end = SQLDateToDate(sliderEnd).getTime();

	var time = (n * (end - start)) / scale; // time in milliseconds
	var d = new Date();
	d.setTime(time + start)
	return parseDate(d);
}

const selectElement2 = document.querySelector('.slider');
function sliderChanged(){
	console.log("Slider moved.");
	date = slider(selectElement2.value);
	load_on_date(date);
}

selectElement2.addEventListener('change', sliderChanged);
