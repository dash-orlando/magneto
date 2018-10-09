@echo off
REM Batch command to guide and automate the setup of Magneto for windows
REM User can quickly install the required python module by just entering the module name
REM Runs on Windows
REM *** NOTE:
REM 	Using set /p var=StringWeWantToPrint<NUL will omit the newline

 
:select
echo.
echo.
echo Please select correct CPU architecture
echo ================
echo 1. 32-bit
echo 2. 64-bit
echo.

set /p x=">\ "
IF "%x%" == "1" (
	GOTO BIT_32
) ELSE (
	IF "%x%" == "2" (
		GOTO BIT_64
	) ELSE (
		GOTO ERROR
	)
)

:ERROR
cls
echo Invalid choice. Please select (1) or (2)!
GOTO select

:BIT_32
echo Download Python 2.7+ 32-bit by following the link below:
echo https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi
echo Hit enter AFTER installing...
echo.
pause >NUL
GOTO INSTALL

:BIT_64
echo Download Python 2.7+ 64-bit by following the link below:
echo https://www.python.org/ftp/python/2.7.15/python-2.7.15.amd64.msi
echo Hit enter AFTER installing...
echo.
pause >NUL
GOTO INSTALL

:INSTALL
echo Download Microsoft Visual C++ Compiler for Python 2.7 (VCPython) by following the link below:
echo https://www.microsoft.com/en-us/download/details.aspx?id=44266
echo Hit enter AFTER installing...
echo.
pause >NUL

REM Upgrade PIP
set /p var=Upgrading PIP...<NUL
python -m pip install --upgrade pip
echo Done
echo.

REM Install Numpy
set /p var=Installing Numpy...<NUL
python -m pip install numpy
echo Done
echo.

REM Install Scipy
set /p var=Installing Scipy...<NUL
python -m pip install scipy
echo Done
echo.

REM Install VTK
set /p var=Installing VTK...<NUL
IF "%x%" == "1" (
	python -m pip install "VTK_win32.whl"
) ELSE (
	python -m pip install "VTK_win64.whl"
)
echo Done
echo.

REM Install MayaVi
set /p var=Installing MayaVi...<NUL
python -m pip install mayavi
echo Done
echo.

REM Install PySerial
set /p var=Installing PySerial...<NUL
python -m pip install pyserial
echo Done
echo.

echo Installation complete!
pause
exit