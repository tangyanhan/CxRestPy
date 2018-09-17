import os
import re
import time

import requests
import json
from requests_toolbelt import MultipartEncoder


class CxRestAPI(object):

    def __init__(self, config_path):
        self.config_path = config_path
        self.server, self.username, self.password = self.get_config()
        self.urls = self.get_urls()
        self.cookies = self.login()
        self.headers = self.cookies.copy()
        self.headers.update({"Accept": "application/json;v=1.0",
                             "api-version": "2.0"})
        pass

    def get_config(self):
        """
        获取配置文件，配置文件在‘etc/config’，请修改相关信息以便脚本可以连接到您的 Checkmarx 服务器。
        :return: List
        """
        try:
            with open(self.config_path + '/config.json') as config:
                conf = json.loads(config.read())
            server = conf.get("server")
            username = conf.get("username")
            password = conf.get("password")
            return server, username, password
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))

    def get_urls(self):
        """
        读取urls.json，请不要随意修改其中的数据。
        :return: Dict
        """
        try:
            with open(self.config_path + "/urls.json") as urls:
                return json.loads(urls.read())
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))

    def send_requests(self, keyword, url_sub=None, headers=None, data=None):
        """

        :param keyword: str     定义从urls中拿哪一个值
        :param url_sub: str     定义urls中形参的值（可选）
        :param headers: dict    定义header（可选）
        :param data: dict       定义body（可选）
        :return: json/text/content
        """
        if url_sub is None:
            url_sub = dict(pattern="", value="")
        try:
            url_parameters = self.urls.get(keyword, None)
            if not url_parameters:
                raise Exception("Keyword not in urls.json")
            url = self.server + re.sub(url_sub.get("pattern"),
                                       url_sub.get("value"),
                                       url_parameters.get("url_suffix"))
            s = requests.Session()
            headers = headers or self.headers
            req = requests.Request(method=url_parameters.get("http_method"),
                                   headers=headers, cookies=self.cookies,
                                   url=url, data=data)
            prepped = req.prepare()
            resp = s.send(prepped)
            if resp.status_code == 200:
                if headers.get("Accept") == "application/json;v=1.0":
                    return resp
                else:
                    return resp
            elif resp.status_code in [201, 202]:
                return resp
            elif resp.status_code == 204:
                return resp
            elif resp.status_code == 400:
                raise Exception(" 400 Bad Request: {}.".format(resp.text))
            elif resp.status_code == 404:
                raise Exception(" 404 Not found {}.".format(resp.text))
            else:
                raise Exception(" Failed: {}.".format(resp.text))

        except Exception as e:
            raise Exception("{}".format(e))

    def get_token(self):
        """
        使用OAuth2.0方式取得令牌。
        :return: dict
                {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGtr0hoV4Vj8GNkyk2A",
                    "expires_in": 86400,
                    "token_type": "Bearer"
                }
        """
        data = {"username": self.username,
                "password": self.password,
                "grant_type": "password",
                "scope": "sast_rest_api",
                "client_id": "resource_owner_client",
                "client_secret": '014DF517-39D1-4453-B7B3-9930C563627C'}
        url = self.server + self.urls.get("token").get("url_suffix")
        token = requests.post(url=url, data=data)
        return token.json()

    def login(self):
        """
        实现登录功能，用于拿到cookie，获得执行后续操作权限。
        :return: dict
                {
                    "cxCookie": cx_cookie,
                    "CXCSRFToken": cx_csrf_token,
                }
        """
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            url = self.server + self.urls.get("login").get("url_suffix")
            r = requests.post(url, data=data)
            if r.status_code == 200:
                cx_cookie = r.cookies.get("cxCookie")
                cx_csrf_token = r.cookies.get("CXCSRFToken")
                return {
                    "cxCookie": cx_cookie,
                    "CXCSRFToken": cx_csrf_token,
                }
            elif r.status_code == 400:
                raise Exception(" 400 Bad Request. ")
            else:
                raise Exception(" login Failed. ")
        except Exception as e:
            raise Exception("Unable to get cookies: {} .".format(e))

    def get_all_teams(self):
        """
        获得所有组的信息。
        :return:list
                [
                    {
                      "id": "00000000-1111-1111-b111-989c9070eb11",
                      "fullName": \\CxServer
                    },
                    {
                        "id": "11111111-2222-448d-b029-989c9070eb22",
                        "fullName": \\CxServer\\SP
                    },
                    {
                        "id": "22222222-2222-448d-b029-989c9070eb22",
                        "fullName": \\CxServer\\SP\\Company
                    },
                    {
                        "id": "22222222-2222-448d-b029-989c9070eb23",
                        "fullName": \\CxServer\\SP\\Company\\Users
                    }
                ]
        """
        keyword = "get_all_teams"
        return self.send_requests(keyword=keyword)

    def get_project_details_by_id(self, project_id):
        """
        获取所有Project的详细信息。
        :param project_id:str
        :return:dict
        """
        keyword = "get_project_details_by_id"
        url_sub = {"pattern": "{project_id}",
                   "value": project_id}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_reports_by_id(self, report_id, report_type):
        """
        获取报告
        :param report_id: str
        :param report_type: str 'pdf','rtf','csv', 'xml'
        :return: str
        """
        keyword = "get_reports_by_id"
        url_sub = {"pattern": "{report_id}",
                   "value": str(report_id)}
        headers = self.headers.copy()
        headers.update({"Accept": "application/"+report_type})
        return self.send_requests(keyword=keyword, url_sub=url_sub, headers=headers)

    def get_report_status_by_id(self, report_id):
        """
        获取报告生成状态
        :param report_id: str
        :return: dict
        """
        keyword = "get_report_status_by_id"
        url_sub = {"pattern": "{report_id}",
                   "value": str(report_id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def set_remote_source_setting_to_git(self, project_id, config_path=None,
                                         git_url=None, branch=None):
        """
        通过 project id 设置 Git
        :param project_id: str
        :param config_path: str
        :param git_url: str
        :param branch: str
        :return: dict
        """
        keyword = "set_remote_source_setting_to_git"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        if config_path is not None:
            try:
                with open(config_path) as f:
                    config = json.loads(f.read())
                git_url = config.get("url")
                branch = config.get("branch")
            except Exception as e:
                raise e
        data = {"id": project_id,
                "Url": git_url,
                "Branch": branch}
        headers = self.headers.update({"Content-Length": "0"})
        return self.send_requests(keyword=keyword, url_sub=url_sub, headers=headers, data=data)

    def set_remote_source_setting_to_svn(self, id):
        keyword = "set_remote_source_setting_to_svn"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def set_remote_source_setting_to_tfs(self, id):
        keyword = "set_remote_source_setting_to_tfs"
        url_sub = {"pattern": "{id}",
                   "value": id}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def set_remote_source_setting_to_shared(self, id):
        keyword = "set_remote_source_setting_to_shared"
        url_sub = {"pattern": "{id}",
                   "value": id}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def set_remote_source_setting_to_perforce(self, id):
        keyword = "set_remote_source_setting_to_perforce"
        url_sub = {"pattern": "{id}",
                   "value": id}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_all_project_details(self):
        """
        获取所有Project信息
        :return:dict
        """
        keyword = "get_all_project_details"
        return self.send_requests(keyword=keyword).json()

    def create_project_with_default_configuration(self, name, owning_team, is_public=True):
        """
        使用默认设置创建一个新Project，请使用Get_all_teams()获取team ID。要更改项目设置，请使用define_sast_scan_settings()。
        :param name:str
        :param owning_team:str
        :param is_public:boolean
        :return:dict
        """
        keyword = "create_project_with_default_configuration"
        data = {"name": name,
                "owningTeam": owning_team,
                "isPublic": is_public}
        return self.send_requests(keyword=keyword, data=data)

    def register_scan_report(self, report_type, scan_id):
        """

        :param report_type:
        :param scan_id:
        :return:
        """
        keyword = "register_scan_report"
        data = {"reportType": report_type,
                "scanId": scan_id}
        return self.send_requests(keyword=keyword, data=data)

    def upload_source_code_zip_file(self, project_id, zip_path):
        keyword = "upload_source_code_zip_file"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        file_name = zip_path.split()[-1]
        files = MultipartEncoder(fields={"zippedSource": (file_name,
                                                          open(zip_path, 'rb'),
                                                          "application/zip")})
        headers = self.headers.copy()
        headers.update({"Content-Type": files.content_type})
        return self.send_requests(keyword=keyword, url_sub=url_sub, headers=headers, data=files)

    def set_remote_source_setting_to_git_using_ssh(self, project_id,
                                                   config_path=None, git_url=None,
                                                   branch=None, private_key=None):
        keyword = "set_remote_source_setting_to_git"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        if config_path is not None:
            try:
                with open(config_path, 'r') as f:
                    f = json.load(f)
                git_url = f.get("url")
                branch = f.get("branch")
                private_key = f.get("privateKey")
            except Exception as e:
                raise e
        id_rsa = open(private_key, 'rb').read()
        data = {"id": project_id,
                "url": git_url,
                "branch": branch,
                "privatekey": id_rsa}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def get_all_engine_server_details(self):
        keyword = "get_all_engine_server_details"
        return self.send_requests(keyword=keyword)

    def register_engine(self, name, uri, minLoc, maxLoc, isBlocked=False):
        """

        :param name: str
        :param uri: str
        :param minLoc: int
        :param maxLoc: int
        :param isBlocked: boolean
        :return: dict
        """
        keyword = "register_engine"
        data = {"name": name,
                "uri": uri,
                "minLoc": minLoc,
                "maxLoc": maxLoc,
                "isBlocked": isBlocked}
        return self.send_requests(keyword=keyword, data=data)

    def unregister_engine_by_engine_id(self, id):
        keyword = "unregister_engine_by_engine_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_engine_details(self, id):
        keyword = "get_engine_details"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def update_engine_server(self, id, name, uri, minLoc, maxLoc, isBlocked=False):
        keyword = "update_engine_server"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        data = {"name": name,
                "uri": uri,
                "minLoc": minLoc,
                "maxLoc": maxLoc,
                "isBlocked": isBlocked}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def get_all_scan_details_in_queue(self):
        keyword = "get_all_scan_details_in_queue"
        return self.send_requests(keyword=keyword)

    def get_all_preset_details(self):
        keyword = "get_all_preset_details"
        return self.send_requests(keyword=keyword)

    def get_sast_scan_details_by_scan_id(self, id):
        keyword = "get_sast_scan_details_by_scan_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_preset_details_by_preset_id(self, preset_id):
        keyword = "get_preset_details_by_preset_id"
        url_sub = {"pattern": "{preset_id}",
                   "value": str(preset_id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_all_engine_configurations(self):
        keyword = "get_all_engine_configurations"
        return self.send_requests(keyword=keyword)

    def get_scan_settings_by_project_id(self, project_id):
        keyword = "get_scan_settings_by_project_id"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_engine_configuration_by_id(self, id):
        keyword = "get_engine_configuration_by_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def define_sast_scan_settings(self, project_id, preset_id, engine_configuration_id):
        keyword = "define_sast_scan_settings"
        data = {"projectId": project_id,
                "presetId": preset_id,
                "engineConfigurationId": engine_configuration_id}
        return self.send_requests(keyword=keyword, data=data)

    def create_new_scan(self, project_id, is_incremental=False, is_public=True, force_scan=True):
        keyword = "create_new_scan"
        data = {"projectId": project_id,
                "isIncremental": is_incremental,
                "isPublic": is_public,
                "forceScan": force_scan}
        return self.send_requests(keyword=keyword, data=data)

    def get_all_osa_scan_details_for_project(self, project_id, page=1, items_per_page=100):
        ## version
        keyword = "get_all_osa_scan_details_for_project"
        data = {"projectId": str(project_id),
                "page": int(page),
                "itemsPerPage": int(items_per_page)}
        return self.send_requests(keyword=keyword, data=data, headers=None)

    def create_an_osa_scan_request(self, project_id, zip_path):
        keyword = "create_an_osa_scan_request"
        file_name = zip_path.split()[-1]
        files = MultipartEncoder(fields={"projectId": str(project_id),
                                         "zippedSource": (file_name,
                                                          open(zip_path, 'rb'),
                                                          "application/zip")})
        # print(files)
        headers = self.headers.copy()
        headers.update({"Content-Type": files.content_type})
        return self.send_requests(keyword=keyword, headers=headers, data=files).json()

    def get_all_osa_file_extensions(self):
        keyword = "get_all_osa_file_extensions"
        return self.send_requests(keyword=keyword).text

    def get_osa_scan_by_scan_id(self, scan_id):
        keyword = "get_osa_scan_by_scan_id"
        url_sub = {"pattern": "{scan_id}",
                   "value": str(scan_id)}
        data = {"sacnId": scan_id}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data).json()

    def get_osa_scan_summary_report(self, scan_id, report_format="PDF"):
        """

        :param scan_id: str
        :param report_format: str  <json, html, pdf>
        :return:
        """
        keyword = "get_osa_scan_summary_report"
        data = {"scanId": str(scan_id),
                "reportFormat": report_format.lower()}
        return self.send_requests(keyword=keyword, data=data)

    def get_osa_licenses_by_id(self, scan_id):
        keyword = "get_osa_licenses_by_id"
        data = {"scanId": str(scan_id)}
        return self.send_requests(keyword=keyword, data=data)

    def get_osa_scan_libraries(self, scan_id):
        keyword = "get_osa_scan_libraries"
        data = {"scanId": str(scan_id)}
        return self.send_requests(keyword=keyword, data=data)

    def get_osa_scan_vulnerabilities_by_id(self, scan_id, page=1, items_per_page=100):
        keyword = "get_osa_scan_vulnerabilities_by_id"
        data = {"scanId": str(scan_id),
                "page": page,
                "itemsPerPage": items_per_page}
        return self.send_requests(keyword=keyword, data=data)

# Checkmarx v8.7.0 add
    def get_all_custom_tasks(self):
        keyword = "get_all_custom_tasks"
        return self.send_requests(keyword=keyword).json()

    def delete_project_by_id(self, id):
        keyword = "delete_project_by_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        data = {"id": int(id),
                "deleteRunningScans": True}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def update_project_name_or_team_id(self, id, name=None, owning_team=None):
        ## version
        keyworld = "update_project_name_or_team_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        if owning_team is None:
            data = {"id": id,
                    "name": name}
        elif owning_team is None:
            data = {"id": id,
                    "owningTeam": owning_team}
        else:
            data = {"id": id,
                    "name": name,
                    "owningTeam": owning_team}
        return self.send_requests(keyword=keyworld, url_sub=url_sub, data=data)

    def get_custom_task_by_id(self, id):
        keyword = "get_custom_task_by_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_all_issue_tracking_systems(self):
        keyword = "get_all_issue_tracking_systems"
        return self.send_requests(keyword=keyword).json()

    def get_issue_tracking_system_details_by_id(self, id):
        keyword = "get_issue_tracking_system_details_by_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def get_project_exclude_settings_by_project_id(self, id):
        keyword = "get_project_exclude_settings_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def set_project_exclude_settings_by_project_id(self, id, settings, folders=None, files=None):
        keyword = "set_project_exclude_settings_by_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        if settings == 'folders':
            data = {"id": str(id),
                    "excludeSettings": settings,
                    "excludeFoldersPattern": folders}
        else:
            data = {"id": str(id),
                    "excludeSettings": settings,
                    "excludeFilesPattern": files}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def get_remote_source_settings_for_git_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_git_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def get_remote_source_settings_for_svn_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_svn_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def get_remote_source_settings_for_tfs_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_tfs_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def get_remote_source_settings_for_custom_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_custom_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def get_remote_source_settings_for_shared_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_shared_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()

    def get_remote_source_settings_for_perforce_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_perforce_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def set_data_retention_settings_by_project_id(self, id, scans_to_keep):
        keyword = "set_data_retention_settings_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        data = {"id": int(id),
                "scansToKeep": scans_to_keep}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def set_issue_tracking_system_as_jira_by_id(self, project_id, system_id, jira_project_id, issue_type_id, fields, field_id, values):
        keyword = "set_issue_tracking_system_as_jira_by_id"
        url_sub = {"pattern": "{id}",
                   "values": str(project_id)}
        data = {"issueTrackingSystemId": int(system_id),
                "jiraProjectId": str(jira_project_id),
                "jiraSettings": {"issueTrackingSystemId": int(system_id),
                                 "jiraProjectId": str(jira_project_id)},
                "issueType": {"id": str(issue_type_id),
                              "fields": {"id": field_id,
                                         "values": values}}}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def get_scan_queue_details_by_scan_id(self, id):
        keyword = "get_scan_queue_details_by_scan_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def update_queued_scan_status_by_scan_id(self, id, status="Cancelled"):
        keyword = "update_queued_scan_status_by_scan_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        data = {"Id": int(id),
                "status": str(status)}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def add_or_update_a_comment_by_scan_id(self, id, content):
        keyword = "add_or_update_a_comment_by_scan_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        data = {"Id": int(id),
                "updatedScanDto": {"Comment": content}}
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data)

    def update_sast_scan_settings(self, project_id, preset_id, engine_configuration_id):
        keyword = "update_sast_scan_settings"
        data = {"projectId": int(project_id),
                "presetId": int(preset_id),
                "engineConfigurationId": engine_configuration_id}
        return self.send_requests(keyword=keyword, data=data)

    def create_project_and_start_a_scan(self, config_path):
        """
        创建一个项目并开始扫描。
        配置文件参考‘etc/project_config.json.template’
        :param config_path:
        :return:
        """
        with open(config_path, 'rb') as f:
            config = json.loads(f.read())
        project = self.create_project_with_default_configuration(name=config.get('name'),
                                                                 owning_team=config.get('owningTeam'),
                                                                 is_public=config.get('isPublic'))
        project_id = project.json().get("id")
        if config.get('projectSetting') == 'local':
            self.upload_source_code_zip_file(project_id=project_id, zip_path=config.get('zipPath'))
        elif config.get('projectSetting') == 'git':
            self.set_remote_source_setting_to_git(project_id=project_id, config_path='etc/git_config')
        preset_id = config.get('presetId')
        engine_configuration_id = config.get('engineConfigurationId')
        self.define_sast_scan_settings(project_id=project_id, preset_id=preset_id,
                                       engine_configuration_id=engine_configuration_id)
        scan = self.create_new_scan(project_id=project_id)
        scan_id = scan.json().get("id")
        while True:
            scan_status = self.get_sast_scan_details_by_scan_id(id=scan_id).json().get('status').get('name')
            if scan_status == 'Finished':
                break
            time.sleep(10)
        report_type = config.get("reportType").upper()
        report = self.register_scan_report(report_type=report_type, scan_id=scan_id)
        report_id = report.json().get('reportId')
        while True:
            report_status = self.get_report_status_by_id(report_id=report_id).json().get("status").get("value")
            if report_status == 'Created':
                break
            time.sleep(5)
        report_name = config.get('name') + '.' + report_type.lower()
        report_outfile = self.get_reports_by_id(report_id=report_id, report_type=report_type).content
        with open(os.path.expanduser(report_name), 'wb') as f:
            f.write(report_outfile)

