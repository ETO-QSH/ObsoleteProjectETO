@echo off
call conda activate %1
"%CONDA_PREFIX%\python.exe" train.py -s "%~2" -m "%~3" --iterations %4 --quiet --port 0 %*
