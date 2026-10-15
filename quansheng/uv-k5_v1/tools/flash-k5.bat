@echo off
setlocal
rem ====================================================================
rem  flash-k5.bat - flashe TACVYR K5 sur un Quansheng UV-K5 / K6 / 5R v1
rem  (cable de programmation K, radio en mode chargement : PTT enfonce
rem  a l'allumage, LED allumee).  Necessite Python 3 et pyserial.
rem    flash-k5.bat            demande le port COM
rem    flash-k5.bat COM5       port donne
rem ====================================================================
cd /d "%~dp0"
set FW=..\firmware\TACVYR-K5_v1.3.bin
set PY=python
where py >nul 2>&1 && set PY=py
%PY% -c "import serial" >nul 2>&1
if errorlevel 1 (
  echo pyserial absent : installation...
  %PY% -m pip install pyserial
)
set PORT=%~1
if "%PORT%"=="" (
  echo Ports serie presents :
  %PY% -c "import serial.tools.list_ports as l; [print('  ', p.device, '-', p.description) for p in l.comports()]"
  set /p PORT=Port du cable ^(ex. COM5^) : 
)
echo.
echo  1. Eteindre la radio
echo  2. L'allumer en tenant PTT enfonce : ecran noir, LED allumee
echo  3. Relacher PTT, puis appuyer sur une touche ici
pause >nul
%PY% k5flash.py %PORT% "%FW%" "*TACVYR-K5 v1.3"
if errorlevel 1 (
  echo.
  echo [ERREUR] flashage non termine : verifier le port, le jack, le mode chargement, puis recommencer.
) else (
  echo.
  echo OK : eteindre puis rallumer la radio. F puis 5 = TACVYR.
)
pause
endlocal
