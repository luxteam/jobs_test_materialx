#!/bin/bash
FILE_FILTER=$1
TESTS_FILTER="$2"
RETRIES=$3

python3.9 -m pip install --user -r ../jobs_launcher/install/requirements.txt
python3.9 ../jobs_launcher/executeTests.py --test_filter $TESTS_FILTER --file_filter $FILE_FILTER --tests_root ../jobs --work_root ../Work/Results --work_dir MaterialX --scale_thumbnails 2.0 --cmd_variables Tool ../materialx/bin/MaterialXView ResPath "$CIS_TOOLS/../TestResources/materialx_autotests_assets" Retries $RETRIES

