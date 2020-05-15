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
          name: "ORDER",
          alias: "Order",
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
        title: "{Name} ({Longitude}, {Latitude})"
      }
    });


    var map = new Map({
      basemap: "streets-navigation-vector",
      layers: [locationLayer]
    });


    var view = new MapView({
      container: "viewDiv",  // DOM element
      map: map,              // map reference
      center: [-77.119244, 38.793095],
      zoom: 15
    });

  //Add Points
  var pointsRenderer = {
            type: "simple",
            symbol: {
                type: "picture-marker",
                url: " http://static.arcgis.com/images/Symbols/NPS/npsPictograph_0096.png",
                width: "18px",
                height: "18px"
            }
        };

        var pointsLabels = {
            symbol: {
                type: "text",
                color: "#FFFFFF",
                haloColor: "#5E8D74",
                haloSize: "2px",
                font: {
                    size: "12px",
                    family: "Noto Sans",
                    style: "italic",
                    weight: "normal"
                }
            },
            labelPlacement: "above-center",
            labelExpressionInfo: {
                expression: "$feature.OBJECTID - 1"
            }
        };

        var popupPoints = {
            "title": "Coco's Trail",
            "content": "<b>Landmark:</b> {NOTES}<br><b>Directions:</b> {DIRECT}<br><b>Type:</b> {NAME}<br><b>Image:</b>"
        }

      //Points Feature Layer
        var landmarksLayer = new FeatureLayer({
            url: "https://services1.arcgis.com/7CPYy0u5Z9IAJ2OG/arcgis/rest/services/Coco_Landmarks/FeatureServer/0",
            renderer: pointsRenderer,
            labelingInfo: [pointsLabels],
            //outFields: ["TRL_NAME","ELEV_FT"],
            popupTemplate: popupPoints
        });

        map.add(landmarksLayer);

  //Add Path

        var pathRenderer = {
            type: "simple",
            symbol: {
                type: "simple-line",
                style: "short-dot",
                color: "#3B2487",
                width: "1px"
            }
        };

        var popupPath = {
            title: "Coco's Trail",
            content: "Follow me on my daily walk!"
        }


        // Path Feature Layer
        var trailsLayer = new FeatureLayer({
            url: "https://services1.arcgis.com/7CPYy0u5Z9IAJ2OG/ArcGIS/rest/services/Lines/FeatureServer/0",
            renderer: pathRenderer,
            popupTemplate: popupPath
        });

        map.add(trailsLayer, 0);

  //Color Polygons
    var simpleFillRenderer = {
      type: "simple",
      symbol: {
        type: "simple-fill",
        color: [245,66,173,0.5],
        outline: {
          color: [255, 255, 255],
          width: 1
        }
      }
    };

    // Pop-up Object Based on Location
    var popupWinslow = {
      expressionInfos: [
        {
          name: "yes-no",
          title: "Yes/No",
          expression: document.getElementById("arcade-test").text
        }
        ],
        content: "This is parcel {PARCEL_KEY}.<br />Are you here? {expression/yes-no}!"
    };

    // Polygon Layer
  //https://www.fairfaxcounty.gov/maps/open-geospatial-data
    var Winslow = new FeatureLayer({
      url: "https://services1.arcgis.com/7CPYy0u5Z9IAJ2OG/arcgis/rest/services/Winslow_Parcels/FeatureServer/0",
      renderer: simpleFillRenderer,
      outFields: ["OBJECTID"],
      popupTemplate: popupWinslow
    });
    map.add(Winslow, 0);

    // Location Widget to find User Location
    var locateWidget = new Locate({
      view: view,
      useHeadingEnabled: false,
      goToOverride: function(view, options) {
        options.target.scale = 1500;
       scale
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

    // Function to get longitude and latitude:
    function showCoordinates(pt) {
      var coords = "Lon/Lat (" + pt.longitude.toFixed(3) +
        ", " + pt.latitude.toFixed(3) + ")";
      coordsWidget.innerHTML = coords;
    }

    // Event Handlers
    view.watch("stationary", function(isStationary) {
      showCoordinates(view.center);
    });

    view.on("pointer-move", function(evt) {
      showCoordinates(view.toMap({ x: evt.x, y: evt.y }));
    });

    // Create a simple coordinates widget for displaying current location
    // https://developers.arcgis.com/labs/javascript/get-map-coordinates/
    var coordsWidget = document.createElement("div");
    coordsWidget.id = "coordsWidget";
    coordsWidget.className = "esri-widget esri-component";
    coordsWidget.style.padding = "7px 15px 5px";
    view.ui.add(coordsWidget, "bottom-right");

  });
