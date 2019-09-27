# M3U-to-Google-Play-Music
Convert local music playlist files from m3u format to become playlists in your Google Play Music library.

This is for those of us that still have libraries of MP3 files and playlists in m3u format.  The m3u playlist format is still a nice way to universally manage playlists and is used by many media players (e.g. Winamp, iTunes).

This is quick and dirty script you can run regularly to:
  - scan a directory of local m3u playlists
  - pull down all playlists you have in Google Play Music
  - compare and identfy what playlists are not in Google
  - grab MP3 tags from local songs and find the IDs of those songs in Google
  - use those IDs to recreate those playlists in Google Play Music

You'll need to go through initial steps to authenticate with Google to ensure it sees your script as one of your authorized devices.  These steps are in the first part of the script.
