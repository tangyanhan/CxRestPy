# Checkmarx REST API SDK
This is a Checkmarx REST API SDK implemented by Python 3.6.

# Environments

Env | Usage
------|------
CX_URL | Checkmarx URL,例如http://example.com/
CX_USERNAME | Username
CX_PASSWORD | Password
CX_PROJECT_NAME | Checkmarx 上的项目名，搞错了分析结果会出现在其它项目里！
CX_EXCLUDES | 分析不包括哪些文件，它们将不会被打包

---
## Getting Started
---
If you want to know more about Checkmarx REST API,please check Checkmarx Knowledge Center：
https://checkmarx.atlassian.net/wiki/spaces/KC/pages/33980523/REST+API
### Prerequisites
* Python package requirements:
> * requests==2.18.4
> * requests-toolbelt==0.8.0

## File structure of this project
```
.
|-- etc
|   |-- config.json
|   |-- git_config.json.template
|   |-- git_config_use_ssh.json.template
|   |-- project_config.json.template
|   `-- urls.json
|
|-- Include
|   `-- ......
|
|-- Lib
|   `-- ......
|
|-- Scripts
|   |-- activate
|   |-- activate.bat
|   |-- activate.ps1
|   |-- activate_this.py
|   |-- chardetect.exe
|   |-- deactivate.bat
|   |-- easy_install-3.6.exe
|   |-- easy_install.exe
|   |-- pip.exe
|   |-- pip3.6.exe
|   |-- pip3.exe
|   |-- python.exe
|   |-- python3.dll
|   |-- python36.dll
|   |-- ythonw.exe
|   `-- wheel.exe
|
|-- tcl
|   `-- ......
|
|-- Create_a_scan_and_get_report.py
|-- pip-selfcheck.json
|-- README.md
|-- requirements.txt
|-- RestAPI.py
|-- test.py
`-- Unit_Test.py
```

## A demo process to ues RestAPI
---
### Windows
```
Win + R  cmd
> cd <The CxREST API Path>
> Scripts/activate.bat
> python Create_a_scan_and_get_report.py
```
### Linux / Unix
```b
open a Terminal
$ cd <the CxREST API Path>
$ ./Scripts/activate
$ python Create_a_scan_and_get_report.py
```

---
## Flow Chart
![avatar](https://raw.githubusercontent.com/binqsoft/CxRestPy/master/Lib/flow_chart.png)

 ## The method list provided in CxREST API

| Method |  UnitTest | |
| :---------- | :----------: | :---------- |
|1.get_config| ok | |
|2.get_urls| ok | |
|3.send_requests| ok | |
|4.get_token| ok | |
|5.login| ok | |
|6.get_all_teams| ok | |
|7.get_project_details_by_id| ok | |
|8.get_reports_by_id| ok | |
|9.get_report_status_by_id| ok | |
|10.set_remote_source_setting_to_git| ok | |
|11.set_remote_source_setting_to_svn| X | need svn support |
|12.set_remote_source_setting_to_tfs| X | need tfs support |
|13.set_remote_source_setting_to_shared| X | need windows shared support |
|14.set_remote_source_setting_to_perforce| X | need perforce support |
|15.get_all_project_details| ok | |
|16.create_project_with_default_configuration| ok | |
|17.register_scan_report| ok | |
|18.upload_source_code_zip_file| ok | |
|19.set_remote_source_setting_to_git_using_ssh| ok | |
|20.get_all_engine_server_details| ok | |
|21.register_engine| ok | |
|22.unregister_engine_by_engine_id| ok | |
|23.get_engine_details| ok | |
|24.update_engine_server| ok | |
|25.get_all_scan_details_in_queue| ok | |
|26.get_all_preset_details| ok | |
|27.get_sast_scan_details_by_scan_id| ok | |
|28.get_preset_details_by_preset_id| ok | |
|29.get_all_engine_configurations| ok | |
|30.get_scan_settings_by_project_id| ok | |
|31.get_engine_configuration_by_id| ok | |
|32.define_sast_scan_settings| ok | |
|33.create_new_scan| ok | |
|34.get_all_osa_scan_details_for_project| ok | |
|35.create_an_osa_scan_request| ok | |
|36.get_all_osa_file_extensions| ok | |
|37.get_osa_scan_by_scan_id| ok | |
|38.get_osa_scan_summary_report| ok | |
|39.get_osa_licenses_by_id| ok | |
|40.get_osa_scan_libraries| ok | |
|41.get_osa_scan_vulnerabilities_by_id| ok | |
|42.get_all_custom_tasks| ok | |
|43.delete_project_by_id| ok | |
|44.update_project_name_or_team_id| ok | |
|45.get_custom_task_by_id| ok | |
|46.get_all_issue_tracking_systems| ok | |
|47.get_issue_tracking_system_details_by_id| ok | |
|48.get_project_exclude_settings_by_project_id| ok | |
|49.set_project_exclude_settings_by_project_id| ok | |
|50.get_remote_source_settings_for_git_by_project_id| ok | |
|51.get_remote_source_settings_for_svn_by_project_id| ok | |
|52.get_remote_source_settings_for_tfs_by_project_id| ok | |
|53.get_remote_source_settings_for_custom_by_project_id| ok | |
|54.get_remote_source_settings_for_shared_by_project_id| ok | |
|55.get_remote_source_settings_for_perforce_by_project_id| ok | |
|56.set_data_retention_settings_by_project_id| ok | |
|57.set_issue_tracking_system_as_jira_by_id| ok | |
|58.get_scan_queue_details_by_scan_id| ok | |
|59.update_queued_scan_status_by_scan_id| ok | |
|60.add_or_update_a_comment_by_scan_id| ok | |
|61.update_sast_scan_settings| ok | |
|62.create_project_and_start_a_scan| ok | |
