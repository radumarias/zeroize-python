set "e=|| exit /b"

pytest %e%
python examples/lock_and_zeroize.py %e%
python examples/zeroize_before_fork.py %e%