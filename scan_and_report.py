import json
import RestAPI
import time
import os

from zip import create_code_zip

def get_project_id(cx, project_name):
    project_list = cx.get_all_project_details()
    for project in project_list:
        if project.get('name') == project_name:
            return project.get('id')
    return None


def main():
    cx_url = os.environ.get('CX_URL')
    if not cx_url:
        print('CX_URL is not set')
        exit(1)

    cx_username = os.environ.get('CX_USERNAME')
    if not cx_username:
        print('CX_USERNAME is not set')
        exit(1)
    cx_password = os.environ.get('CX_PASSWORD')
    if not cx_password:
        print('CX_PASSWORD is not set')
        exit(1)

    d = {
        'server': cx_url + 'CxRestAPI',
        'username': cx_username,
        'password': cx_password
    }

    config_dir = os.environ.get('CX_CONFIG_DIR')
    if not config_dir:
        config_dir = './etc'
    config_path = config_dir + '/config.json'
    with open(config_path, 'w') as outfile:
        json.dump(d, outfile)
    
    cx = RestAPI.CxRestAPI(config_dir)

    global project_name, team_id
    project_name = os.environ.get('CX_PROJECT_NAME')
    if not project_name:
        print('CX_PROJECT_NAME is not set')
        exit(1)

    project_id = get_project_id(cx, project_name)

    if not project_id:
        print('Failed to get project id with project name:', project_name)
        exit(1)

    cx_excludes = os.environ.get('CX_EXCLUDES')
    if cx_excludes:
        excludes = cx_excludes.split(',')
    create_code_zip(excludes)
    zip_path = '/tmp/code.zip'
    report_types = ["PDF", "RTF", "CSV", "XML"]
    report_code = 0
    cx.upload_source_code_zip_file(project_id=project_id, zip_path=zip_path)
    print("* Creating a new scan...")
    scan = cx.create_new_scan(project_id)
    scan_id = scan.json().get("id")
    while True:
        scan_status = cx.get_sast_scan_details_by_scan_id(id=scan_id).json().get("status").get("name")
        print("\tScan status：[", scan_status, "]", end=" ")
        if scan_status == "Finished":
            print()
            break
        print("Re-Check after 10s ...")
        time.sleep(10)
    print("* Creating report...")
    report_type = report_types[report_code].lower()
    report = cx.register_scan_report(report_type=report_type, scan_id=scan_id)
    report_id = report.json().get("reportId")
    while True:
        report_status = cx.get_report_status_by_id(report_id).json().get("status").get("value")
        print("\tReport status：[", report_status, "]", end=" ")
        if report_status == "Created":
            print()
            break
        print("Re-Check after 5s ...")
        time.sleep(5)
    report_name = project_name + "." + report_type
    reports = cx.get_reports_by_id(report_id, report_type).content
    with open(os.path.expanduser(report_name), 'wb') as f:
        f.write(reports)
    print("* Successful! Thanks for use. *")


if __name__ == '__main__':
    main()
