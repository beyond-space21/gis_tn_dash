function convert4326To3857(lat, lon) {
    // Convert the coordinates
    const [x, y] = proj4('EPSG:4326', 'EPSG:3857', [lon, lat]);
    return { x, y };
}

  function getTileCoordinates(lat, lon, zoom) {
    const { x, y } = convert4326To3857(lat, lon);

    const tileSize = 256; // Size of each tile in pixels
    const initialResolution = 2 * Math.PI * 6378137 / tileSize; // Resolution at zoom level 0
    const resolution = initialResolution / Math.pow(2, zoom);

    const tileX = Math.floor((x + 20037508.3427892) / (resolution * tileSize));
    const tileY = Math.floor((20037508.3427892 - y) / (resolution * tileSize));

    const pixelX = Math.floor(((x + 20037508.3427892) % (resolution * tileSize)) / resolution);
    const pixelY = Math.floor(((20037508.3427892 - y) % (resolution * tileSize)) / resolution);

    return { tile:{col: tileX, row: tileY, zoom:zoom}, pixel:{x:pixelX,y:pixelY}};
}


function update_metrics(sw_lat,ne_lat,sw_lng,ne_lng){
    
    let minLat = sw_lat
    let maxLat = ne_lat
    let minLon = sw_lng
    let maxLon = ne_lng
    const R = 6371; // Radius of the Earth in kilometers
    // Convert the latitude and longitude differences to radians
    const toRad = (deg) => deg * (Math.PI / 180);
    const latDiff = toRad(maxLat - minLat);
    const lonDiff = toRad(maxLon - minLon);
    // Calculate the area in square kilometers (approximating Earth's curvature)
    const latDistance = R * latDiff;  // Distance in km along latitude
    const lonDistance = R * Math.cos(toRad((maxLat + minLat) / 2)) * lonDiff;  // Distance in km along longitude
    const area = latDistance * lonDistance; // Area in square kilometers
    document.getElementById('area').innerText = area.toFixed(2) + " Sq Km"


    p1 = getTileCoordinates(sw_lat,sw_lng,18)
    p2 = getTileCoordinates(ne_lat,ne_lng,18)
    console.log(p1,p2);
    col = p2.tile.col - p1.tile.col + 1
    row = p1.tile.row - p2.tile.row + 1
    document.getElementById('tiles').innerText = col*row
    document.getElementById('pixels').innerText = col*row*256*256
    RAM_VALIDATOR = Math.round((col*row*256*256) / (1024 * 1024 * 1024))*4
    document.getElementById('ram').innerText = RAM_VALIDATOR + " GB"; 

    
}

