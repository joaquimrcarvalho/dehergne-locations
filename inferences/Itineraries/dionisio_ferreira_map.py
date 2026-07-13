#!/usr/bin/env python3
"""
Generate a map of Dionísio Ferreira's journey and locations.
"""

import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# Location data for Dionísio Ferreira
# Format: (name, lat, lon, description, date, color, icon)
locations = [
    # Birthplace
    (
        "Lisbon, Portugal",
        38.7223,
        -9.1393,
        "Born: October 9/10, 1720",
        "1720",
        "green",
        "home",
    ),
    # Early career
    (
        "? (Entered Jesuits)",
        None,
        None,
        "Entered Jesuits: February 5, 1738<br>Location unknown",
        "1738",
        "blue",
        "info-sign",
    ),
    # Voyage to China
    (
        "? (Embarked for China)",
        None,
        None,
        "Embarked: 1745 (Wicki #1908, Voyage 164)",
        "1745",
        "orange",
        "arrow-right",
    ),
    ("? (Arrived China)", None, None, "Arrived: 1745", "1745", "orange", "arrow-right"),
    # China mission
    (
        "Ko-li-tsem, Kiating, Kiangnan<br>(Jiading, Jiangsu)",
        31.3833,
        121.2500,
        "Mission station: 1745-1753<br>Resided at 'Ko-li-tsem' in Kiating area<br>Wikidata: Q662101 (Kiating)",
        "1745-1753",
        "blue",
        "info-sign",
    ),
    (
        "Ko-li-tsem, Kiating, Kiangnan",
        31.3833,
        121.2500,
        "<b>CAPTURED: December 8, 1753</b><br>Arrested at his mission station",
        "1753-12-08",
        "red",
        "remove",
    ),
    # Exile to Macau
    (
        "Macau",
        22.1987,
        113.5439,
        "Exiled: 1756<br>Wikidata: Q14773",
        "1756",
        "orange",
        "arrow-right",
    ),
    (
        "Macau",
        22.1987,
        113.5439,
        "Took 4 vows: May 3, 1756",
        "1756-05-03",
        "blue",
        "info-sign",
    ),
    (
        "Macau",
        22.1987,
        113.5439,
        "<b>ARRESTED: July 5, 1762</b>",
        "1762-07-05",
        "red",
        "remove",
    ),
    # Return to Portugal - Imprisonment
    (
        "Lisbon (Forte de S. Julião)",
        38.7223,
        -9.1393,
        "Imprisoned: October 19, 1764 - September 6, 1767<br>Fort St. Julian (political prison)<br>Wikidata: Q597 (Lisbon)",
        "1764-1767",
        "red",
        "remove",
    ),
    # Deportation to Italy
    (
        "Italy",
        41.8719,
        12.5674,
        "Deported: 1767<br>Wikidata: Q38",
        "1767",
        "orange",
        "arrow-right",
    ),
    # Death
    (
        "Castel Gandolfo, Italy",
        41.7483,
        12.6490,
        "<b>DIED: March 22, 1771</b><br>Near Rome<br>Wikidata: Q242105",
        "1771-03-22",
        "black",
        "remove",
    ),
]

# Create the map centered on Europe/Asia
m = folium.Map(location=[30.0, 60.0], zoom_start=3, tiles="CartoDB positron")

# Add title
folium.Marker(
    location=[50.0, 60.0],
    icon=folium.DivIcon(
        icon_size=(500, 50),
        icon_anchor=(250, 0),
        html='<div style="font-size: 16pt; font-weight: bold; text-align: center; color: #2c3e50;">Dionísio Ferreira (1720-1771)<br>From Lisbon to China and Back</div>',
    ),
).add_to(m)

# Filter out locations with unknown coordinates
known_locations = [
    loc for loc in locations if loc[1] is not None and loc[2] is not None
]
route_points = []

# Add markers for each location with known coordinates
for i, (name, lat, lon, description, date, color, icon) in enumerate(known_locations):
    # Create popup content
    popup_content = f"""
    <div style="font-family: Arial; min-width: 250px;">
        <h4 style="margin: 0; color: #2c3e50;">{name}</h4>
        <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
        <p style="margin: 5px 0;">{description}</p>
    </div>
    """

    # Add marker
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_content, max_width=350),
        tooltip=f"{name} ({date})",
        icon=folium.Icon(color=color, icon=icon, prefix="glyphicon"),
    ).add_to(m)

    route_points.append([lat, lon])

# Draw the route line (great circle for long distances)
from folium import plugins

# Create route with ant path for visual effect
if len(route_points) > 1:
    # Draw lines between consecutive points
    for i in range(len(route_points) - 1):
        folium.PolyLine(
            locations=[route_points[i], route_points[i + 1]],
            color="#e74c3c",
            weight=2,
            opacity=0.6,
            dash_array="5, 10",
        ).add_to(m)

# Add legend
legend_html = """
<div style="position: fixed; 
            bottom: 50px; right: 50px; 
            background-color: white; 
            padding: 15px; 
            border: 2px solid #2c3e50;
            border-radius: 5px;
            z-index: 1000;
            font-family: Arial;">
    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">Legend</h4>
    <div style="margin: 5px 0;">
        <span style="background-color: green; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Birthplace (1720)
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: blue; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Mission/Activity
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: orange; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Travel/Exile
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: red; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Capture/Prison
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: black; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Death (1771)
    </div>
    <div style="margin: 10px 0 0 0; font-size: 0.9em; color: #666;">
        <em>Dashed line shows approximate route</em>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_file = "dionisio_ferreira_map.html"
m.save(output_file)

print(f"Map saved to: {output_file}")
print(f"\nMap includes {len(known_locations)} locations with coordinates")
print(f"Note: Some locations (entry to Jesuits, embarkation) have unknown coordinates")

# Try to open the map automatically
if os.path.exists(output_file):
    print(f"\n✓ Map successfully created!")
    print(f"File size: {os.path.getsize(output_file)} bytes")
