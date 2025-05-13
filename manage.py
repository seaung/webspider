import os
import sys
import signal
import logging
import argparse

from typing import Any

from app import create_app


def setup_logger(log_level: str) -> None:
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("webspier.log"),
        ]
    )


def signal_handler(signum: Any, frame: Any) -> None:
    """信号处理函数"""
    logger = logging.getLogger(__name__)
    logger.info(f"收到信号 {signum} 正在优雅退出...")
    sys.exit(0)


def parse_options() -> argparse.ArgumentParser:
    """解析命令行选项"""
    parser = argparse.ArgumentParser(description="web 爬虫可视化管理服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务监听地址")
    parser.add_argument("--port", default=9331, help="""服务端口(孟德尔9331定律，
                        恐怖的豌豆射手，支配了我高中三年!!!)""")
    parser.add_argument("--env", default='development',
                        choices=['development', 'production', 'testing'],
                        help='运行环境')
    parser.add_argument("--debug", action="store_true", help="是否开启调试模式")
    parser.add_argument("--log-level", default="INFO", choices=[
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL",
    ], help="日志级别")

    return parser.parse_args()


def main() -> None:
    """程序服务入口函数"""
    options = parse_options()

    os.environ["FLASK_ENV"] = options.env

    # 配置日志等级
    setup_logger(options.log_level)
    logger = logging.getLogger(__name__)

    # 注册信号
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app = create_app()

    # 启动日志信息设置
    logger.info(
        f"web spider manager服务启动, 监听地址为 : {options.host}:{options.port}")
    logger.info(f"运行环境为 : {options.env}")
    logger.info(f"调试模式为  : {options.debug}")

    try:
        app.run(
            host=options.host,
            port=options.port,
            debug=options.debug,
        )
    except Exception as e:
        logger.error(f"服务器启动失败 {str(e)}")
        sys.exit(1)
    except InterruptedError:
        logger.warning("shutdown this server...")
        exit(1)


if __name__ == "__main__":
    main()
