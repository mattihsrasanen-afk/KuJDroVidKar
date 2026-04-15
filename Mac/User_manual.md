📸🎥 Photos and Videos on Map - User Guide

This software is designed for browsing and managing media files (photos and videos) on an interactive map. It also allows you to edit the GPS locations of your files directly into their EXIF metadata and track recorded routes from videos.
1. User Interface Overview

The screen is divided into three main sections:

    Left Panel (Local Area / Lähialue): Displays a list of the files currently visible within the map's viewport. This list updates automatically as you move or zoom the map.

    Center Section (Map and Media): An interactive map where your media files appear as markers (photos as orange dots, videos as camera icons). The large image viewer and video player also open in this area.

    Right Panel (Settings & Filtering): Contains API key management, folder selection, map filtering tools, and a complete list of all loaded files.

2. Map Functions and Layers

You can change the map background using the layer menu in the top right corner.

    Map Layers: Available options include OpenStreetMap, as well as the National Land Survey of Finland's (MML) topographic map, background map, aerial photo, and simplified map (selkokartta).

    Property Boundaries: You can enable MML property boundaries (requires zooming in closely).

    Historical Aerial Photos: If your files contain metadata with years (e.g., 2010–2026), historical aerial photos for those specific years will automatically appear in the layer menu.

    Note: Using MML layers requires an API key (see Section 7).

3. Browsing Photos and Videos

    Preview (PiP - Picture in Picture): Hovering your mouse over a map marker opens a small pop-up window showing a preview of the image. The corresponding file is also highlighted in the side panel list.

    Opening an Image: Click a map marker or a file name in the list to open the image in the large viewer (Lightbox). If multiple photos share the exact same location, you can browse through them using the arrow keys or the on-screen navigation buttons. Press Esc or the X button to close the viewer.

    Playing a Video: Clicking a video marker opens the video player on top of the map.

4. Video Player and Drone Routes

If a video contains GPS route data, a red line will be drawn on the map.

    Route Tracking: As the video plays, a yellow "drone arrow" moves along the map, displaying the camera's real-time location and viewing angle.

    Mini-Map: A floating mini-map at the bottom right of the video closely tracks the location. You can drag the mini-map to a different spot or resize it by dragging its bottom-right corner.

    Fullscreen: The "⛶ Suurenna" (Enlarge) button expands the video to fill the screen. In this mode, you can move the video player itself by dragging its title bar.

5. Filtering (Right Panel)

You can easily hide or show files on the map and in the lists:

    By Location: Show all (Kaikki), only those with a saved GPS location (Sijainti), or only those missing a location (Ei sijaintia).

    By Type: Show all (Kaikki), only JPG images, only videos, or other files.

6. Editing Locations (EXIF Saving)

You can move photos to new locations on the map. The new coordinates are saved directly to the files' metadata (this requires the backend server to be running).

Method A: Moving a Single Photo

    Hover over the photo you want to move.

    Click "📍 Siirrä kuvapiste" (Move image point) in the preview window.

    Drag the target marker that appears to the correct location on the map.

    Click "Tallenna EXIF-tietoihin" (Save to EXIF data) in the bottom menu (or Peruuta to cancel).

Method B: Moving Multiple Photos (Multi-selection mode)

    Check the "🎯 Monivalintatila" (Multi-selection mode) box in the right panel.

    Click on the map or in the lists to select the photos you want to move. Selected photos will turn purple.

    Click "📍 Siirrä vapaasti" (Move freely) in the menu that appears at the bottom. Drag the large target to a new location and save.

    Alternative (Merging): With photos selected, hover over another (unselected) photo and click "🔗 Yhdistä valitut tähän" (Merge selected here). This moves all selected photos directly to that specific photo's coordinates.

7. Settings and Folder Management (Right Panel)

    MML API Key: Enter your National Land Survey API key and click "Tallenna" (Save). This enables highly accurate Finnish topographic maps, property boundaries, and aerial photos. Refresh the page (F5) after saving to apply the layers.

    Adding a Folder: Click "➕ Lisää kansio hiirellä" (Add folder with mouse) to open your system's folder selection window, allowing you to load new photos and videos into the application.

8. Supporting Development

The top bar of the application contains links if you wish to support the developer (Matti Räsänen).

    PayPal: A direct link for a PayPal donation.

    Crypto Donation (Kryptolahjoitus): Clicking this opens a window with QR codes and wallet addresses for supporting the project via Bitcoin (BTC), Ethereum (ETH), or Solana (SOL).
