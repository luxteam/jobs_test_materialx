import argparse
import os
import json
import platform
from datetime import datetime
from shutil import copyfile
import sys
import traceback
import win32api
from time import time
from time import sleep
import utils

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import *
from jobs_launcher.core.system_info import get_gpu


def copy_test_cases(args):
    copyfile(os.path.realpath(os.path.join(os.path.dirname(
        __file__), '..', 'Tests', args.test_group, 'test_cases.json')),
        os.path.realpath(os.path.join(os.path.abspath(
            args.output), 'test_cases.json')))

    with open(os.path.join(os.path.abspath(args.output), "test_cases.json"), "r") as json_file:
        cases = json.load(json_file)

    if os.path.exists(args.test_cases) and args.test_cases:
        with open(args.test_cases) as file:
            test_cases = json.load(file)['groups'][args.test_group]
            if test_cases:
                necessary_cases = [
                    item for item in cases if item['case'] in test_cases]
                cases = necessary_cases

        with open(os.path.join(args.output, 'test_cases.json'), "w+") as file:
            json.dump(cases, file, indent=4)


def copy_baselines(args, case, baseline_path, baseline_path_tr):
    try:
        copyfile(os.path.join(baseline_path_tr, case['case'] + CASE_REPORT_SUFFIX),
                 os.path.join(baseline_path, case['case'] + CASE_REPORT_SUFFIX))

        with open(os.path.join(baseline_path, case['case'] + CASE_REPORT_SUFFIX)) as baseline:
            baseline_json = json.load(baseline)

        for thumb in [''] + THUMBNAIL_PREFIXES:
            if os.path.exists(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path'])):
                copyfile(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path']),
                         os.path.join(baseline_path, baseline_json[thumb + 'render_color_path']))
    except:
        main_logger.error('Failed to copy baseline ' +
                                      os.path.join(baseline_path_tr, case['case'] + CASE_REPORT_SUFFIX))


def prepare_empty_reports(args, current_conf):
    main_logger.info('Create empty report files')

    baseline_path_tr = os.path.join(
        'c:/TestResources/materialx_autotests_baselines', args.test_group)

    baseline_path = os.path.join(
        args.output, os.path.pardir, os.path.pardir, os.path.pardir, 'Baseline', args.test_group)

    if not os.path.exists(baseline_path):
        os.makedirs(baseline_path)
        os.makedirs(os.path.join(baseline_path, 'Color'))

    copyfile(os.path.abspath(os.path.join(args.output, '..', '..', '..', '..', 'jobs_launcher',
                                          'common', 'img', 'error.jpg')), os.path.join(args.output, 'Color', 'failed.jpg'))

    with open(os.path.join(os.path.abspath(args.output), "test_cases.json"), "r") as json_file:
        cases = json.load(json_file)

    for case in cases:
        if utils.is_case_skipped(case, current_conf):
            case['status'] = 'skipped'

        if case['status'] != 'done' and case['status'] != 'error':
            if case["status"] == 'inprogress':
                case['status'] = 'active'
            elif case["status"] == 'inprogress_observed':
                case['status'] = 'observed'

            test_case_report = RENDER_REPORT_BASE.copy()
            test_case_report['render_time'] = 0.0
            test_case_report['execution_time'] = 0.0
            test_case_report['test_case'] = case['case']
            test_case_report['render_device'] = get_gpu()
            test_case_report['script_info'] = case['script_info']
            test_case_report['test_group'] = args.test_group
            test_case_report['tool'] = 'HdRPR'
            test_case_report['date_time'] = datetime.now().strftime(
                '%m/%d/%Y %H:%M:%S')

            if 'jira_issue' in case:
                test_case_report['jira_issue'] = case['jira_issue']

            if case['status'] == 'skipped':
                test_case_report['test_status'] = 'skipped'
                test_case_report['file_name'] = case['case'] + case.get('extension', '.jpg')
                test_case_report['render_color_path'] = os.path.join('Color', test_case_report['file_name'])
                test_case_report['group_timeout_exceeded'] = False

                try:
                    skipped_case_image_path = os.path.join(args.output, 'Color', test_case_report['file_name'])
                    if not os.path.exists(skipped_case_image_path):
                        copyfile(os.path.join(args.output, '..', '..', '..', '..', 'jobs_launcher', 
                            'common', 'img', 'skipped.jpg'), skipped_case_image_path)
                except OSError or FileNotFoundError as err:
                    main_logger.error(f"Can't create img stub: {str(err)}")
            else:
                test_case_report['test_status'] = 'error'
                test_case_report['file_name'] = 'failed.jpg'
                test_case_report['render_color_path'] = os.path.join('Color', 'failed.jpg')

            case_path = os.path.join(args.output, case['case'] + CASE_REPORT_SUFFIX)

            if os.path.exists(case_path):
                with open(case_path) as f:
                    case_json = json.load(f)[0]
                    test_case_report['number_of_tries'] = case_json['number_of_tries']

            with open(case_path, 'w') as f:
                f.write(json.dumps([test_case_report], indent=4))

        copy_baselines(args, case, baseline_path, baseline_path_tr)
    with open(os.path.join(args.output, 'test_cases.json'), 'w+') as f:
        json.dump(cases, f, indent=4)


def save_results(args, case, cases, test_case_status, execution_time = 0.0):
    with open(os.path.join(args.output, case["case"] + CASE_REPORT_SUFFIX), "r") as file:
        test_case_report = json.loads(file.read())[0]
        test_case_report["file_name"] = case["case"] + case.get("extension", '.jpg')
        test_case_report["test_status"] = test_case_status
        test_case_report["render_time"] = 0.0
        test_case_report["execution_time"] = execution_time
        test_case_report["execution_log"] = os.path.join("execution_logs", case["case"] + ".log")
        test_case_report["testing_start"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        test_case_report["number_of_tries"] += 1

        if test_case_status == "error":
            stub_image_path = os.path.join(args.output, 'Color', test_case_report['file_name'])
            if not os.path.exists(stub_image_path):
                copyfile(os.path.join(args.output, '..', '..', '..', '..', 'jobs_launcher', 
                    'common', 'img', 'error.jpg'), stub_image_path)

        test_case_report["render_color_path"] = os.path.join("Color", test_case_report["file_name"])
        test_case_report["group_timeout_exceeded"] = False

    with open(os.path.join(args.output, case["case"] + CASE_REPORT_SUFFIX), "w") as file:
        json.dump([test_case_report], file, indent=4)

    if test_case_status != "error":
        case["status"] = test_case_status
        with open(os.path.join(args.output, "test_cases.json"), "w") as file:
            json.dump(cases, file, indent=4)


def execute_tests(args, current_conf):
    rc = 0

    with open(os.path.join(os.path.abspath(args.output), "test_cases.json"), "r") as json_file:
        cases = json.load(json_file)

    for case in [x for x in cases if not utils.is_case_skipped(x, current_conf)]:
        case_start_time = time()

        current_try = 0

        log_path = os.path.join(args.output, "execution_logs")
        utils.create_case_logger(case["case"], log_path)

        while current_try < args.retries:
            execution_time = 0.0

            try:
                utils.case_logger.info(f"Start \"{case['case']}\" (try #{current_try})")
                utils.case_logger.info(f"Screen resolution: width = {win32api.GetSystemMetrics(0)}, height = {win32api.GetSystemMetrics(1)}")

                extension = extension if "extension" in case else "jpg"
                image_path = os.path.abspath(os.path.join(args.output, "Color", f"{case['case']}.{extension}"))
                utils.case_logger.info(f"Image path: {image_path}")

                # existing image can affect retry of case
                if os.path.exists(image_path):
                    os.remove(image_path)

                execution_script = os.path.abspath(args.tool_path)
                script_path = os.path.join(args.output, "{}.bat".format(case["case"]))

                utils.open_tool(script_path, execution_script)

                if "mesh_path" in case:
                    mesh_path = os.path.join(args.res_path, case["mesh_path"])
                    utils.load_mesh(mesh_path)

                if "material_path" in case:
                    material_path = os.path.join(args.res_path, case["material_path"])
                    utils.load_material(material_path)

                if "environment_path" in case:
                    environment_path = os.path.join(args.res_path, case["environment_path"])
                    utils.load_environment(environment_path)

                if "enable_environment_drawing" in case and case["enable_environment_drawing"]:
                    utils.enable_environment_drawing()

                sleep(5)

                utils.save_image(image_path)

                execution_time = time() - case_start_time

                if case["status"] == "active":
                    save_results(args, case, cases, "passed", execution_time = execution_time)
                else:
                    save_results(args, case, cases, "observed", execution_time = execution_time)

                utils.case_logger.info(f"Case \"{case['case']}\" finished")

                break
            except Exception as e:
                execution_time = time() - case_start_time

                if case["status"] == "active":
                    save_results(args, case, cases, "error", execution_time = execution_time)
                else:
                    save_results(args, case, cases, "observed", execution_time = execution_time)

                utils.case_logger.error(f"Failed to execute test case (try #{current_try}): {str(e)}")
                utils.case_logger.error(f"Traceback: {traceback.format_exc()}")
            finally:
                current_try += 1

                utils.post_action()

                utils.case_logger.info("Post actions finished")
        else:
            utils.case_logger.error(f"Failed to execute case \"{case['case']}\" at all")
            rc = -1
            execution_time = time() - case_start_time

            if case["status"] == "active":
                save_results(args, case, cases, "error", execution_time = execution_time)
            else:
                save_results(args, case, cases, "observed", execution_time = execution_time)

    return rc


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", required=True, metavar="<dir>")
    parser.add_argument("--tool_path", required=True)
    parser.add_argument("--test_group", required=True)
    parser.add_argument("--res_path", required=True)
    parser.add_argument("--test_cases", required=True)
    parser.add_argument("--retries", required=False, default=2, type=int)

    return parser


if __name__ == "__main__":
    main_logger.info("simpleRender start working...")

    args = createArgsParser().parse_args()

    try:
        os.makedirs(args.output)

        if not os.path.exists(os.path.join(args.output, "Color")):
            os.makedirs(os.path.join(args.output, "Color"))
        if not os.path.exists(os.path.join(args.output, "execution_logs")):
            os.makedirs(os.path.join(args.output, "execution_logs"))

        render_device = get_gpu()
        system_pl = platform.system()
        current_conf = set(platform.system()) if not render_device else {platform.system(), render_device}
        main_logger.info(f"Detected GPUs: {render_device}")
        main_logger.info(f"PC conf: {current_conf}")
        main_logger.info("Creating predefined errors json...")

        copy_test_cases(args)
        prepare_empty_reports(args, current_conf)
        exit(execute_tests(args, current_conf))
    except Exception as e:
        main_logger.error(f"Failed during script execution. Exception: {str(e)}")
        main_logger.error(f"Traceback: {traceback.format_exc()}")
        exit(-1)
