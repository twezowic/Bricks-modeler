set LDVIEW_EXE="D:\LEGO\LDView\LDView64.exe"

for %%a in ( ".\dat\*.dat" ) do %LDVIEW_EXE% "%%a" "-SaveSnapshot=%%~na.png" -PreferenceSet=mine -SaveActualSize=0 -SaveImageType=1 -SaveZoomToFit=1 -SaveWidth=400 -SaveHeight=400 -DefaultZoom=0.95 -FOV=10 -DefaultMatrix=-DefaultMatrix=0.707107,0,0.707107,0.353553,0.866025,-0.353553,-0.612373,0.5,0.612372