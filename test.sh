#!/bin/bash

set -e

pytest
python examples/lock_and_zeroize.py
python examples/zeroize_before_fork.py
