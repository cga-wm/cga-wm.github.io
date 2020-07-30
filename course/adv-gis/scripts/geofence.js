require([
  "esri/Map",
  "esri/views/MapView",
  "esri/widgets/Locate",
  "esri/Graphic",
  "esri/renderers/UniqueValueRenderer",
  "esri/layers/FeatureLayer",
  "esri/widgets/Editor",
  "esri/symbols/SimpleMarkerSymbol",
  "esri/symbols/SimpleLineSymbol",
  "esri/Color"
], function(Map, MapView, Locate, Graphic, UniqueValueRenderer, FeatureLayer, Editor, SimpleMarkerSymbol, SimpleLineSymbol, Color) {

    // Create an empty feature layer for storing locator points
    // (also use this for Editor points)
    var locationLayer = new FeatureLayer({
    // create an instance of esri/layers/support/Field for each field object
      title: "My Locations",
      fields: [
        {
          name: "ObjectID",
          alias: "ObjectID",
          type: "oid"
        },
        {
          name: "NAME",
          alias: "Name",
          type: "string"
        },
        {
          name: "WITHIN",
          alias: "Inside Geofence",
          type: "integer"
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
        title: "{NAME} ({WITHIN})"
      }
    });

    // Alternative renderer for Williamsburg
    // GOAL: get this to change colors based on geofence
    var uniqueValRenderer = new UniqueValueRenderer({
      valueExpression: document.getElementById("arcade-geofence").text,
      valueExpressionTitle: "Geofence Test",
      defaultSymbol: {
        type: "simple-marker",
        color: "green"
      },
      uniqueValueInfos: [{
        value: "inside",
        symbol: {
          type: "simple-marker",
          color: "blue"
        },
        label: "are"
      }, {
        value: "outside",
        symbol: {
          type: "simple-marker",
          color: "red"
        },
        label: "are not"
      }]
    });

    locationLayer.renderer = uniqueValRenderer;

    // Create a map for adding layers to
    // https://developers.arcgis.com/javascript/latest/api-reference/esri-Map.html
    var map = new Map({
      basemap: "streets-navigation-vector",
      layers: [locationLayer]
    });

    // Create a MapView for rendering the map and widgets
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
      //title: "Geofence Test",
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

    // The location widget used to find a user's location
    // NOTE: this may use Google Geolocation API, which has daily limits!
    var locateWidget = new Locate({
      view: view,
      useHeadingEnabled: false,
      goToOverride: function(view, options) {
        options.target.scale = 1500;  // Override the default map scale
        return view.goTo(options.target);
      }
    });

    // Create an empty array for storing a user's location
    var graphics = [];

    // Create an event listener for when the locate button is clicked
    locateWidget.on("locate", function(evt) {
      // Debugging; you can view this from a webpage's console
      console.log("Caught locate event trigger!");
      console.log(evt);
      console.log("Latitude is: ", evt.position.coords.latitude);
      console.log("Longitude is: ", evt.position.coords.longitude);

      // Scrub location from position object:
      var data = {
        NAME: "My Location",
        WITHIN: 0
      };

      var graphic = new Graphic({
        geometry: {
          type: "point",
          latitude: evt.position.coords.latitude,
          longitude: evt.position.coords.longitude
        },
        attributes: data
      });

      // Add the point geometry to the array
      graphics.push(graphic);

      // Add our array of point geometries to an object with the keyword
      // for adding features; this is used by the applyEditsToLayer
      const addEdits = {
        addFeatures: graphics
      };
      applyEditsToLayer(addEdits);
    });

    // Function pulled directly from arcgis.developers tutorial
    // https://developers.arcgis.com/javascript/latest/sample-code/layers-featurelayer-collection-edits/index.html
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

    // Add editor widget (issues with running over daily limit on geolocate)
    // https://developers.arcgis.com/javascript/latest/api-reference/esri-widgets-Editor.html
    var editorWidget = new Editor({
      view: view
    });
    view.ui.add(editorWidget, "top-right");

    // Create a function to get longitude and latitude:
    function showCoordinates(pt) {
      var coords = "Lon/Lat (" + pt.longitude.toFixed(3) +
        ", " + pt.latitude.toFixed(3) + ")";
      coordsWidget.innerHTML = coords;
    }

    // Add event handlers to update map coordinates
    view.watch("stationary", function(isStationary) {
      showCoordinates(view.center);
    });

    view.on("pointer-move", function(evt) {
      showCoordinates(view.toMap({ x: evt.x, y: evt.y }));
    });

    // Create a simple coordinates widget for displaying current location
    // NOTE: adds a div to the DOM
    // https://developers.arcgis.com/labs/javascript/get-map-coordinates/
    var coordsWidget = document.createElement("div");
    coordsWidget.id = "coordsWidget";
    coordsWidget.className = "esri-widget esri-component";
    coordsWidget.style.padding = "7px 15px 5px";
    view.ui.add(coordsWidget, "bottom-right");

  });
