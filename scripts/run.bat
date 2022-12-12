set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set RETRIES=%3

if not defined RETRIES set RETRIES=2
if not defined UPDATE_REFS set UPDATE_REFS="No"
if not defined TOOL set TOOL="..\USD\build\bin\usdview"
if not defined PYTHON set PYTHON="C:\Python37\python.exe"

python -m pip install -r ..\jobs_launcher\install\requirements.txt
python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir MaterialX --cmd_variables Tool ..\materialx\bin\MaterialXView.exe ResPath "C:\TestResources\materialx_autotests_assets" Retries %RETRIES%