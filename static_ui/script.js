ip_tg = document.getElementById("fileInput")
up_btn = document.getElementById("up_btn")

up_btn.onclick = () => {
    ip_tg.click()
}

endpoint = "http://84.247.139.36:5000/"

ip_tg.addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(e.target.result, "application/xml");
            const coordinatesElements = xmlDoc.getElementsByTagName("coordinates");

            let coordinatesArray = [];
            for (let i = 0; i < coordinatesElements.length; i++) {
                const rawCoordinates = coordinatesElements[i].textContent.trim();
                const parsedCoordinates = rawCoordinates.split(/\s+/).map(coord => {
                    const [longitude, latitude, altitude] = coord.split(',').map(Number);
                    return { longitude, latitude, altitude }; // Optional: Use altitude if needed
                });
                coordinatesArray.push(...parsedCoordinates);
            }

            var pol = [];
            for (var i = 0; i < coordinatesArray.length; i++) {
                lat = coordinatesArray[i].latitude
                lng = coordinatesArray[i].longitude
                pol.push({ lat: lat, lng: lng })
            }

            rst = getBoundingBox(pol)
            resetWithKML(rst, pol)

        };
        reader.readAsText(file);
    }
});


function getBoundingBox(latLonArray) {

    let minLat = Infinity;
    let maxLat = -Infinity;
    let minLon = Infinity;
    let maxLon = -Infinity;

    console.log(latLonArray);

    for (var i = 0; i < latLonArray.length; i++) {
        lat = latLonArray[i].lat
        lng = latLonArray[i].lng
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
        if (lng < minLon) minLon = lng;
        if (lng > maxLon) maxLon = lng;
    }

    return {
        ne: { lat: maxLat, lng: maxLon },
        sw: { lat: minLat, lng: minLon }
    };
}

function put_log(str) {
    document.getElementById("server_response").innerText += '\n> ' + str
}

async function update_met(){
    const response = await fetch(endpoint + "/api/bsd", {
        headers: {
            "Content-Type": "application/json",
            "Auth-Token": await getToken()
        },
    });

    const data = await response.json();
    document.getElementById('ram_usd').innerText = Math.round(data.ram / (1024 * 1024)) + " MB"
    document.getElementById('tasks_sz').innerText = data.tasks

    document.getElementById('tasks_list').innerHTML = ""
    keys = Object.keys(data.tasks_list)
    keys.forEach(e => {
        elm = document.createElement('div')
        elm.className = "tsks_lst " + data.tasks_list[e].status
        elm.innerText = e
        elm.onclick = () => {
            window.open(endpoint + "/get_file.html?" + e)
        }
        document.getElementById('tasks_list').appendChild(elm)
    });
}

setInterval(async () => {
    await update_met()
}, 2000);

function generateUUID() {
    // Generate a UUID (Version 4)
    let d = new Date().getTime();
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid.replace(/-/g, ''); // Remove hyphens
}

btn_flg = true

document.getElementById('run_btn').onclick = async () => {
    if (btn_flg) {
        btn_flg = false
        if (rectangle) {
            const bounds = rectangle.getBounds();
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();

            box_data = {
                ne_lat: ne.lat(),
                ne_lon: ne.lng(),
                sw_lat: sw.lat(),
                sw_lon: sw.lng(),
                task_id: generateUUID()
            }

            box_data = {
                ne_lat: 11.07124,
                ne_lon: 77.011059,
                sw_lat: 11.070540,
                sw_lon: 77.00447,
                task_id: generateUUID()
            }

            await fetch(endpoint + "/process_data", {
                method: "POST",
                body: JSON.stringify(box_data),
                headers: {
                    "Content-type": "application/json; charset=UTF-8",
                    "Auth-Token": await getToken()
                }
            })
                .then((response) => response.json())
                .then((json) => console.log(json));
                
            await update_met()

            setTimeout(() => {
                btn_flg = true
            }, 2000);

        } else {
            alert("No rectangle to run.");
        }
    } else {
        alert("Wait some SECONDS to process previous request")
    }
}

