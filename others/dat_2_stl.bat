@echo off

set sourcedir=D:\LEGO\parts
set exportdir=D:\LEGO_MOJE\parts_obj

for %%f in ("%sourcedir%\*.dat") do (
    echo File: %%~nxf
    "D:\LEGO\LDView\LDView64.exe" -ExportFile="%exportdir%\%%~nf.stl" "%%f"
)