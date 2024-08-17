function set_markers() {
    /*
        function to declare the markers of buildings we have information for 
        Updates Needed: have a DB where the data is coming from
    */
    ///////////////// Data
    let markers = ['University of Waterloo', 'Icon 330', 'Society 145'];
    let marker_location = {
        'University of Waterloo': { lat: 43.4723, lng: -80.5449 },
        'Icon 330': { lat: 43.4757587, lng: -80.5387263 }, 
        'Society 145': { lat: 43.4767823, lng: -80.5383641 }   
    };
    /////////////////////

    for (let i = 0; i < markers.length; i++) {
        // Add an interactive marker with a custom icon
        var marker = new google.maps.Marker({
            position: marker_location[markers[i]],
            map: map,
            title: markers[i],
            icon: 'https://maps.google.com/mapfiles/kml/shapes/info-i_maps.png' // Custom icon URL
        });

        // Create the content for the InfoWindow
        var infoContent = `<div><h3>${markers[i]}</h3><p>Some additional information about ${markers[i]}</p></div>`;

        // Create a new InfoWindow
        var infoWindow = new google.maps.InfoWindow({
            content: infoContent
        });

        // Add a click listener to the marker to open the InfoWindow
        google.maps.event.addListener(marker, 'click', (function(marker, infoWindow) {
            return function() {
                infoWindow.open(map, marker);
            };
        })(marker, infoWindow));
    }
}