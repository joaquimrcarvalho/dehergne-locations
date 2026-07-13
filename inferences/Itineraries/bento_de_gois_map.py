#!/usr/bin/env python3
"""
Generate a map of Bento de Góis's journey and locations.
This script creates an interactive HTML map with all locations associated with Bento de Góis.
"""

import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# Location data for Bento de Góis
# Format: (name, lat, lon, description, date)
locations = [
    # Birthplace
    (
        "Vila Franca do Campo, Azores",
        37.7167,
        -25.4333,
        "Birthplace<br>Born: 1563",
        "1563",
    ),
    # Early career (India)
    (
        "Índia (India)",
        20.5937,
        78.9629,
        "Stayed as soldier before 1584<br>Entered Jesuits: 1584, 1588",
        "<1584",
    ),
    # Mission to Mughal Empire
    (
        "Lahore (Lahora), Pakistan",
        31.5204,
        74.3587,
        "Arrived at Akbar's court: 1598<br>Took vows: June 13, 1598",
        "1598",
    ),
    (
        "Agra, India",
        27.1767,
        78.0081,
        "Stayed until Oct 29, 1602<br>Ambassador of Akbar",
        "1601-1602",
    ),
    # Journey to China
    (
        "Lahore, Pakistan",
        31.5204,
        74.3587,
        "Departed for Cathay: Oct 29, 1602<br>Passed through: Dec 8, 1602",
        "1602",
    ),
    ("Pamir Mountains", 38.5, 73.5, "Crossed before Nov 1603", "1603"),
    (
        "Yarkand (Shache), China",
        38.4164,
        77.2452,
        "Arrived: End of November 1603",
        "1603",
    ),
    (
        "Turpan (Tourphan), China",
        42.9477,
        89.1785,
        "Passed through after Nov 1603",
        ">1603",
    ),
    ("Hami, China", 42.8250, 93.5150, "Arrived: October 17, 1605", "1605"),
    (
        "Kia-yu-louan (Jiayuguan), China",
        39.8000,
        98.2167,
        "Passed through after Oct 1605",
        ">1605",
    ),
    (
        "Suchow (Suzhou/Jiuquan), China",
        39.7320,
        98.4942,
        "Arrived: December 22, 1605<br><b>Died: April 11, 1607</b>",
        "1605-1607",
    ),
]

# Create the map centered on Central Asia
m = folium.Map(location=[35.0, 70.0], zoom_start=4, tiles="CartoDB positron")

# Add title
folium.Marker(
    location=[45.0, 60.0],
    icon=folium.DivIcon(
        icon_size=(400, 50),
        icon_anchor=(200, 0),
        html='<div style="font-size: 18pt; font-weight: bold; text-align: center; color: #2c3e50;">Bento de Góis (1563-1607)<br>Journey from Portugal to China</div>',
    ),
).add_to(m)

# Create a feature group for the route
route_points = []

# Add markers for each location
for i, (name, lat, lon, description, date) in enumerate(locations):
    # Create popup content
    popup_content = f"""
    <div style="font-family: Arial; min-width: 200px;">
        <h4 style="margin: 0; color: #2c3e50;">{name}</h4>
        <p style="margin: 5px 0;"><strong>Date:</strong> {date}</p>
        <p style="margin: 5px 0;">{description}</p>
    </div>
    """

    # Different colors for different types of locations
    if i == 0:  # Birthplace
        color = "green"
        icon = "home"
    elif i == len(locations) - 1:  # Death place
        color = "red"
        icon = "remove"
    elif i < 4:  # India/Mughal period
        color = "blue"
        icon = "info-sign"
    else:  # Journey to China
        color = "orange"
        icon = "arrow-right"

    # Add marker
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_content, max_width=300),
        tooltip=name,
        icon=folium.Icon(color=color, icon=icon, prefix="glyphicon"),
    ).add_to(m)

    route_points.append([lat, lon])

# Draw the route line
folium.PolyLine(
    locations=route_points, color="#e74c3c", weight=3, opacity=0.7, dash_array="10, 10"
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
        Birthplace (1563)
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: blue; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        India/Mughal Period (1584-1602)
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: orange; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Journey to China (1602-1605)
    </div>
    <div style="margin: 5px 0;">
        <span style="background-color: red; padding: 2px 8px; border-radius: 3px; color: white;">●</span> 
        Death (1607)
    </div>
    <div style="margin: 10px 0 0 0; font-size: 0.9em; color: #666;">
        <em>Dashed line shows approximate route</em>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
output_file = "bento_de_gois_map.html"
m.save(output_file)

print(f"Map saved to: {output_file}")
print(f"Open this file in a web browser to view the interactive map.")

# Try to open the map automatically
if os.path.exists(output_file):
    print(f"\nMap successfully created!")
    print(f"File size: {os.path.getsize(output_file)} bytes")

    # Optionally open in browser
    # webbrowser.open('file://' + os.path.realpath(output_file))
