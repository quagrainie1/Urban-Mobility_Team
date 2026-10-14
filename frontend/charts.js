// summary cards
fetch("api/summary").then(function (r) {return r.json(); }).then(function (d) {
  document.getElementById("c-trips").textContent = d.trips.toLocaleString();
  document.getElementById("c-fare").textContent = "$" + d.avg_fare.toFixed(2);
  document.getElementById("c-dist").textContent = d.avg_distance.toFixed(2) + "mi";
  document.getElementById("c-dur").textContent = d.avg_duration.toFixed(1) + "min";
});

//trips per hour
fetch("/api/hourly").then(function (r) { return r.json(); }).then(function (rows) {
  new Chart(document.getElementById("hourChart"), {
    type: "bar",
    data: {
      labels: rows.map(function (r) { return r.hour; }),
      datasets: [{ label: "Trips", data: rows.map(function (r) { return r.trips; }) }]
    }
  })
})

fetch("/api/zones").then(function(r){return r.json(); }).then(function(d) {
  var m = document.getElementById('map');
  var max = Math.max.apply(null, d.map(function(x){ return x.trips;}));
  var html = '';
  d.forEach(function(row){
    var w = row.trips / max * 100;
    html += '<div style="display:flex;gap:8px;margin:4px"><span style="width:60px">Zone '+row.zone_name+'</span><div style="background:#fbbf24;height: 16px;width:'+w+'%"></div><span>'+row.trips+'</span></div>';
  });
  m.innerHTML = html;
  m.style.height = 'auto';
});

//top routes table
// fetch("/api/top-routes").then(r=>r.json()).then(d=>{
//   let html = "";
//   d.forEach(row=>{
//     html += "<tr><td>" + row.pickup + "</td><td" + row.dropoff + "</td><td>" + row.trips + "</td></tr";
//   });
//   document.querySelector("#routes tbody").innerHTML = html;
// });