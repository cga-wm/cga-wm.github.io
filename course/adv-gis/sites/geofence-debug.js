
//Compare two arrays. True if arrays contain equal contents (regardless of order), false otherwise.
//a1, a2: arrays.
function arraysEqual(a1,a2) {
    a1.sort();
    a2.sort();
    
    if(a1.length != a2.length) return false;
    for(i = 0; i < a1.length; i++){
	if(a1[i] != a2[i]) return false;
    }
    return true;
}

require([
    "esri/Map",
    "esri/views/MapView",
    "esri/layers/FeatureLayer",
    "esri/popup/content/AttachmentsContent",
    "esri/widgets/Track",
    "esri/geometry/Point",
],
	function(
	    Map, 
	    MapView,
	    FeatureLayer,
	    AttachmentsContent,
	    Track,
	    Point,
	    Graphic,
	    geometryEngine
	) {
	    
	    var map = new Map({
		basemap: "topo-vector"
	    });
	    
	    var view = new MapView({
		container: "viewDiv",
		map: map,
		center: [-73.975261,40.691191],
		zoom: 17
	    });
	    
	    //Set up our geofence layer

	    // Define a popup for points of interest
	    var popupPOI = {
		title: "{Name}",
		content: [
		    {
			type: "text",
			text: "{InfoText}"
		    },
		    // Add our attachments to it
		    {
			type: "media",
			mediaInfos: [{
			    type: "image",
			    value: {
				sourceURL: "{ATTACHMENT_URL}"
			    }
			}]
		    }
		]
	    }
            
	    // Create the layer and set the renderer
	    var pointsOfInterest = new FeatureLayer({
		url: "https://services1.arcgis.com/7CPYy0u5Z9IAJ2OG/arcgis/rest/services/ZONE/FeatureServer/0?token=4QLamZchAWDWOyYTrcDhFI-6QMMuT8M-zdCIt77mcsF8an9td64sx8aWBI8nmPMW-tR05MvCpoBwqqQlW-FlphpIquO_Rjjv3pSWXKlqNsRrFwZTq3bxEyBarxXHDAXaVfrsq_xrkahVD5aH2KhYKpeT8J4xckwTNyJUjEK26xWfusjhCT8ANNCZADRFCEQWaCgxBVpLrpIq7i4aczUyZK5eTUuUepx892AcbLSGui6lp1iWawbFvFyYp393NMRb5IRWMNYx0aR3GJ49r2nwhw..",
		outFields: ["Name","InfoText","GlobalID","ATTACHMENT_URL"],
		popupTemplate: popupPOI
	    });
	    
	    // Add the layer
	    map.add(pointsOfInterest,0);


	    //Time to set up our interactive popups.
	    
	    //Let's set it so that you can't click to view popups
	    view.popup.autoOpenEnabled = false;


	    var lastIntersected = null;


	    //For debug purposes: a "click" event version of the "track" event.
	    view.on("click",function(event) {
		
		var query = pointsOfInterest.createQuery();
		query.geometry = event.mapPoint;
		query.spatialRelationship = "intersects";
		query.returnGeometry = false;
		query.outFields = ["OBJECTID"];
		
		pointsOfInterest.queryFeatures(query)
		    .then(function(response){
			console.log(response.features);
			var objectIDs = [];
			for (feature of response.features){
			    objectIDs.push(feature.attributes.OBJECTID);
			}
			//console.log(objectIDs)
			
			if(lastIntersected == null || !arraysEqual(objectIDs,lastIntersected)){
			    lastIntersected = objectIDs;
			    //console.log("new feature set")
			    //console.log(lastIntersected);
			    view.popup.open({
				location: event.mapPoint,
				fetchFeatures: true
			    });
			}
		    });
	    });
	});
	
