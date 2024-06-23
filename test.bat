pytest
if ($LASTEXITCODE) exit $LASTEXITCODE

python examples/lock_and_zeroize.py
if ($LASTEXITCODE) exit $LASTEXITCODE

python examples/zeroize_before_fork.py
if ($LASTEXITCODE) exit $LASTEXITCODE

python examples/mlock.py
if ($LASTEXITCODE) exit $LASTEXITCODE
