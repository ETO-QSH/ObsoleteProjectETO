@echo off
call conda activate %1
"%CONDA_PREFIX%\python.exe" convert.py -s %2
