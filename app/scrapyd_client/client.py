from typing import Any, Dict, List, Optional, Union
import requests
import json
import logging
from urllib.parse import urljoin
from app.config.settings import SCRAPYD_URL


class ScrapydClient:
    """Scrapyd客户端类，用于与Scrapyd API交互"""
    
    def __init__(self, target=SCRAPYD_URL):
        """初始化Scrapyd客户端
        
        Args:
            target (str, optional): Scrapyd服务URL. Defaults to SCRAPYD_URL.
        """
        self.target = target.rstrip('/')
        self.logger = logging.getLogger('ScrapydClient')
    
    def _request(self, endpoint: str, method: str = 'get', **kwargs) -> Dict[str, Any]:
        """发送请求到Scrapyd API
        
        Args:
            endpoint (str): API端点
            method (str, optional): 请求方法. Defaults to 'get'.
            **kwargs: 请求参数
            
        Returns:
            Dict[str, Any]: API响应
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        url = urljoin(self.target, endpoint)
        try:
            if method.lower() == 'get':
                response = requests.get(url, params=kwargs)
            else:
                response = requests.post(url, data=kwargs)
            
            if response.status_code != 200:
                self.logger.error(f"API请求失败: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"HTTP错误: {response.status_code}"}
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # 某些API返回纯文本而非JSON
                return {"status": "ok", "data": response.text}
                
        except requests.RequestException as e:
            self.logger.error(f"请求异常: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def list_projects(self) -> List[str]:
        """列出爬虫项目
        
        Returns:
            List[str]: 项目名称列表
        """
        response = self._request('listprojects.json')
        return response.get('projects', [])
    
    def list_spiders(self, project: str) -> List[str]:
        """列出指定项目的爬虫列表
        
        Args:
            project (str): 项目名称
            
        Returns:
            List[str]: 爬虫名称列表
        """
        response = self._request('listspiders.json', project=project)
        return response.get('spiders', [])
    
    def schedule(self, project: str, spider: str, settings: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """调度爬虫运行
        
        Args:
            project (str): 项目名称
            spider (str): 爬虫名称
            settings (Optional[Dict[str, Any]], optional): 爬虫设置. Defaults to None.
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 包含作业ID的响应
        """
        data = {"project": project, "spider": spider}
        
        # 添加设置参数
        if settings:
            for setting_name, setting_value in settings.items():
                data[f'setting={setting_name}'] = setting_value
        
        # 添加其他参数
        data.update(kwargs)
        
        return self._request('schedule.json', 'post', **data)
    
    def list_jobs(self, project: str) -> Dict[str, List[Dict[str, Any]]]:
        """列出指定项目的工作列表
        
        Args:
            project (str): 项目名称
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 包含pending、running和finished作业的字典
        """
        response = self._request('listjobs.json', project=project)
        return {
            "pending": response.get('pending', []),
            "running": response.get('running', []),
            "finished": response.get('finished', [])
        }
    
    def cancel(self, project: str, job_id: str) -> Dict[str, Any]:
        """取消指定作业
        
        Args:
            project (str): 项目名称
            job_id (str): 作业ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        return self._request('cancel.json', 'post', project=project, job=job_id)
    
    def logs(self, project: str, spider: str, job_id: str, log_type: str = 'log') -> str:
        """获取作业日志
        
        Args:
            project (str): 项目名称
            spider (str): 爬虫名称
            job_id (str): 作业ID
            log_type (str, optional): 日志类型 ('log' 或 'err'). Defaults to 'log'.
            
        Returns:
            str: 日志内容
        """
        response = self._request(f'logs/{project}/{spider}/{job_id}.{log_type}')
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        return str(response)
    
    def daemon_status(self) -> Dict[str, Any]:
        """获取Scrapyd守护进程状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return self._request('daemonstatus.json')
    
    def delete_project(self, project: str) -> Dict[str, Any]:
        """删除项目
        
        Args:
            project (str): 项目名称
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        return self._request('delproject.json', 'post', project=project)
    
    def delete_version(self, project: str, version: str) -> Dict[str, Any]:
        """删除项目版本
        
        Args:
            project (str): 项目名称
            version (str): 版本号
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        return self._request('delversion.json', 'post', project=project, version=version)
    
    def list_versions(self, project: str) -> List[str]:
        """列出项目版本
        
        Args:
            project (str): 项目名称
            
        Returns:
            List[str]: 版本列表
        """
        response = self._request('listversions.json', project=project)
        return response.get('versions', [])
    
    def get_job_stats(self, project: str, job_id: str) -> Dict[str, Any]:
        """获取作业统计信息
        
        Args:
            project (str): 项目名称
            job_id (str): 作业ID
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        jobs = self.list_jobs(project)
        
        # 在所有作业列表中查找指定作业
        for status, job_list in jobs.items():
            for job in job_list:
                if job.get('id') == job_id:
                    return {
                        "status": status,
                        "job": job
                    }
        
        return {"status": "not_found", "message": f"作业 {job_id} 未找到"}
    
    def get_job_items(self, project: str, spider: str, job_id: str) -> Dict[str, Any]:
        """获取作业采集的数据项
        
        Args:
            project (str): 项目名称
            spider (str): 爬虫名称
            job_id (str): 作业ID
            
        Returns:
            Dict[str, Any]: 数据项信息
        """
        response = self._request(f'items/{project}/{spider}/{job_id}.jl')
        if isinstance(response, dict) and 'data' in response:
            # 尝试解析JSON Lines格式
            items = []
            for line in response['data'].strip().split('\n'):
                if line:
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            return {"status": "ok", "items": items}
        return {"status": "error", "message": "无法获取数据项"}


# 创建默认客户端实例
client = ScrapydClient()


# 为了向后兼容，保留函数接口
def list_projects() -> List[str]:
    return client.list_projects()


def list_spiders(project: str) -> List[str]:
    return client.list_spiders(project)


def schedule_spider(project: str, spider: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return client.schedule(project=project, spider=spider, settings=settings or {})


def list_jobs(project: str) -> Dict[str, List[Dict[str, Any]]]:
    return client.list_jobs(project)


def cancel_job(project: str, job_id: str) -> Dict[str, Any]:
    return client.cancel(project, job_id)


def get_job_log(project: str, spider: str, job_id: str, log_type: str = 'log') -> str:
    return client.logs(project, spider, job_id, log_type)


def get_daemon_status() -> Dict[str, Any]:
    return client.daemon_status()


def delete_project(project: str) -> Dict[str, Any]:
    return client.delete_project(project)


def delete_version(project: str, version: str) -> Dict[str, Any]:
    return client.delete_version(project, version)


def list_versions(project: str) -> List[str]:
    return client.list_versions(project)


def get_job_stats(project: str, job_id: str) -> Dict[str, Any]:
    return client.get_job_stats(project, job_id)


def get_job_items(project: str, spider: str, job_id: str) -> Dict[str, Any]:
    return client.get_job_items(project, spider, job_id)
