set PATH=c:\python39\;c:\python39\scripts\;%PATH%
set FILE_FILTER=%1
set TESTS_FILTER="%2"
set RETRIES=%3

python -m pip install -r ..\jobs_launcher\install\requirements.txt
python ..\jobs_launcher\executeTests.py --test_filter %TESTS_FILTER% --file_filter %FILE_FILTER% --tests_root ..\jobs --work_root ..\Work\Results --work_dir MaterialX --scale_thumbnails 2.0 --cmd_variables Tool ..\materialx\bin\MaterialXView.exe ResPath "C:\TestResources\materialx_autotests_assets" Retries %RETRIES%