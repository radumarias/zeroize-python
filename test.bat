pytest
if %errorlevel% neq 0 exit /b %errorlevel%

python examples/lock_and_zeroize.py
if %errorlevel% neq 0 exit /b %errorlevel%

python examples/mlock.py
if %errorlevel% neq 0 exit /b %errorlevel%
