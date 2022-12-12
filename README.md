# Autotests for HdRPR


## MaterialX location
    Download and unpack MaterialX in the `materialx` folder.


## Install
 1. Clone this repo

 2. Get `jobs_launcher` as git submodule, using next commands
 `git submodule init`
 `git submodule update`

 4. Put folders with scenes in `C:/TestResources/materialx_autotests_assets` and baselines in `C:/TestResources/materialx_autotests_baselines`.
 
    ***You should use the specific scenes which defined in `test_cases.json` files in `jobs/Tests/` folders.***

 6. Run `run.bat` from the `scripts` folder with customised arguments with space separator:

    | NUMBER | NAME            | DEFINES                                                                              | DEFAULT                                                                |
    |--------|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------|
    | 1      | FILE_FILTER     | Path to json-file with groups of test to execute                                     | There is no default value                                              |
    | 2      | TESTS_FILTER    | Paths to certain tests from `..\Tests`. If `FILE_FILTER` is set, you can write `""`. | There is no default value                                              |
    | 3      | RETRIES         | Number of retries for each test case.                                                | 2                                                                      |

    Example:
    > run.bat none General

    ***ATTENTION!***

    **The order of the arguments is important. You cannot skip arguments.**
