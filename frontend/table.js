// table.js - Top 10 busiest routes
async function loadTable() {
  try {
    let res =await fetch('/api/top-routes');
    let data = await res.json();
    console.log('Routes loaded', data);

    let html = "";
    data.forEach(row => {
      html += "<tr><td>" + row.pickup + "</td><td>" + row.dropoff + "</td><td>" + row.trips + "</td></tr>";
    });
    document.querySelector("#routes tbody").innerHTML = html;
  } catch (e) {
    console.log('Routes failed', e);
  }
}

loadTable();
