"use client";

import { useState, useCallback } from 'react';
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.webpack.css";
import "leaflet-defaulticon-compatibility";

import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from "react-leaflet";
import { fetchHouses } from "@utils"; // Adjust the import path
import { MapHouses } from "@components";

function ZoomLogger() {
  const [houses, setHouses] = useState<any[]>([]); // Adjust the type according to your data
  const [loading, setLoading] = useState<boolean>(false);
  const map = useMapEvents({
    zoomend: () => fetchMapData(), // Use the function after its declaration
    moveend: () => fetchMapData()  // Use the function after its declaration
  });

  const fetchMapData = useCallback(async () => {
    setLoading(true);

    const bounds = map.getBounds();
    const { lat: lat_tl, lng: long_tl } = bounds.getNorthWest();
    const { lat: lat_br, lng: long_br } = bounds.getSouthEast();

    const filters = {
      page: 1, // Adjust as needed
      limit: 24,
      lat_tl,
      long_tl,
      lat_br,
      long_br
    };

    <MapHouses />
    
  }, [map]);

  return (
    <>
      {loading && <div>Loading...</div>}
      {/* Render the houses data here */}
      {/* Example: */}
      <div>
        {houses.map(house => (
          <div key={house.id}>{house.name}</div>
        ))}
      </div>
    </>
  );
}

export default function Map() {
  return (
    <MapContainer
      preferCanvas={true}
      center={[10.773081, 106.6829]}
      zoom={14}
      scrollWheelZoom={true}
      style={{ height: "50dvh", width: "95%", margin: "auto" }}
    >
      <TileLayer
        attribution=''
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
      />
      <Marker position={[10.773081, 106.6829]}>
        <Popup>
          This Marker icon is displayed correctly with <i>leaflet-defaulticon-compatibility</i>.
        </Popup>
      </Marker>
      <ZoomLogger />
    </MapContainer>
  );
}
