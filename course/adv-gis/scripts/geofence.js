require([
  "esri/Map",
  "esri/views/MapView",
  "esri/widgets/Locate",
  "esri/Graphic",
  "esri/renderers/UniqueValueRenderer",
  "esri/layers/FeatureLayer"
  ], function(Map, MapView, Locate, Graphic, UniqueValueRenderer, FeatureLayer) {

    // https://developers.arcgis.com/javascript/latest/api-reference/esri-Map.html
    var map = new Map({
      basemap: "streets-navigation-vector"
    });

    // A look at Williamsburg, VA
    // point reference: https://en.wikipedia.org/wiki/Williamsburg%2C_Virginia
    // https://developers.arcgis.com/javascript/latest/api-reference/esri-views-MapView.html
    var view = new MapView({
      container: "viewDiv",  // DOM element
      map: map,              // map reference
      center: [-76.706944, 37.270833],
      zoom: 12
    });

    // Simple Fill Renderer (used to color Williamsburg)
    var simpleFillRenderer = {
      type: "simple",
      symbol: {
        type: "simple-fill",
        color: [227, 139, 79, 0.8],  // orange, opacity 80%
        outline: {
          color: [255, 255, 255],
          width: 1
        }
      }
    };

    // Pop-up Object
    var popupWbgh = {
      title: "Geofence Test",
      // FUNCTION
      // content: function(){
      //     return "This parcel is in the {Neighborho} neighborhood.";
      // }
      //
      // ARCADE
      expressionInfos: [
        {
          name: "yes-no",
          title: "Yes/No",
          expression: document.getElementById("arcade-test").text
        }
        ],
        content: "This parcel is in the {Neighborho} neighborhood.<br />Are you here? {expression/yes-no}!"
    };

    // Create an empty feature layer for storing locator points
    const locationLayer = new FeatureLayer({
      // create an instance of esri/layers/support/Field for each field object
      title: "My Locations",
      fields: [
        {
          name: "ObjectID",
          alias: "ObjectID",
          type: "oid"
        },
        {
          name: "Name",
          alias: "Name",
          type: "string"
        },
        {
          name: "Longitude",
          alias: "Lon",
          type: "single"
        },
        {
          name: "Latitude",
          alias: "Lat",
          type: "single"
        }
      ],
      objectIdField: "ObjectID",
      geometryType: "point",
      spatialReference: { wkid: 4326 },  // WGS84
      source: [], // adding an empty feature collection
      renderer: {
        type: "simple",
        symbol: {
          type: "simple-marker",
          color: [0, 0, 255],
          outline: {
            color: [0, 0, 0],
            width: 0.5
          }
        }
      },
      popupTemplate: {
        title: "{Name} ({Longitude}, {Latitude})"
      }
    });
    map.add(locationLayer);

    // Create a polygon feature layer of Williamsburg Parcels
    // data ref: https://data-williamsburg.opendata.arcgis.com/
    // https://developers.arcgis.com/javascript/latest/api-reference/esri-layers-FeatureLayer.html
    var williamsburg = new FeatureLayer({
      url: "https://services1.arcgis.com/7CPYy0u5Z9IAJ2OG/arcgis/rest/services/CityGdb_DBO_Parcels1/FeatureServer/0",
      renderer: simpleFillRenderer,
      outFields: ["Neighborho"],
      popupTemplate: popupWbgh
    });
    map.add(williamsburg, 0);

    // The location widget
    var locateWidget = new Locate({
      view: view,
      useHeadingEnabled: false,
      goToOverride: function(view, options) {
        options.target.scale = 1500;  // Override the default map scale
        return view.goTo(options.target);
      }
    });

    var graphics = []; // empty array for storing locations

    // Create an event listener for when the locate button is clicked
    locateWidget.on("locate", function(evt) {
      console.log("Caught locate event trigger!");
      console.log(evt);
      console.log("Latitude is: ", evt.position.coords.latitude);
      console.log("Longitude is: ", evt.position.coords.longitude);

      // Scrub location from position object:
      var data = {
        LATITUDE: evt.position.coords.latitude,
        LONGITUDE: evt.position.coords.longitude,
        NAME: "Test Point"
      };

      var graphic = new Graphic({
        geometry: {
          type: "point",
          latitude: data.LATITUDE,
          longitude: data.LONGITUDE
        },
        attributes: data
      });

      graphics.push(graphic);

      // addEdits object tells applyEdits that you want to add the features
      const addEdits = {
        addFeatures: graphics
      };
      // apply the edits to the layer
      applyEditsToLayer(addEdits);
    });

    function applyEditsToLayer(edits) {
      locationLayer
      .applyEdits(edits)
      .then(function(results) {
        // if features were added - call queryFeatures to return
        //    newly added graphics
        if (results.addFeatureResults.length > 0) {
          var objectIds = [];
          results.addFeatureResults.forEach(function(item) {
            objectIds.push(item.objectId);
          });
          // query the newly added features from the layer
          locationLayer
          .queryFeatures({
            objectIds: objectIds
          })
          .then(function(results) {
            console.log(
              results.features.length,
              "features have been added."
            );
          });
        }
      })
      .catch(function(error) {
        console.log(error);
      });
    }

    // Add location widget to screen.
    view.ui.add(locateWidget, "top-left");

    // Maybe log the point everytime the locate button is triggered
    // Then make a list of points that you could map and test
    // whether they intersect...


  });
