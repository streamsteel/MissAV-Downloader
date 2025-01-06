from flask import Flask, request, render_template_string, redirect, url_for
import miyuki  # 导入 miyuki 模块
import argparse  # 用于创建 argparse.Namespace 对象
import os

app = Flask(__name__)

# 定义 miyuki 命令的选项
MIYUKI_OPTIONS = {
    "urls": {"type": "list", "help": "Movie URLs, separate multiple URLs with spaces"},
    "auth": {"type": "list", "help": "Username and password, separate with space"},
    "plist": {"type": "str", "help": "Public playlist URL"},
    "limit": {"type": "str", "help": "Limit the number of downloads"},
    "search": {"type": "str", "help": "Movie serial number"},
    "file": {"type": "str", "help": "File path"},
    "proxy": {"type": "str", "help": "HTTP(S) proxy"},
    "ffmpeg": {"type": "bool", "help": "Enable ffmpeg processing"},
    "cover": {"type": "bool", "help": "Download video cover"},
    "ffcover": {"type": "bool", "help": "Set cover as preview (ffmpeg required)"},
    "noban": {"type": "bool", "help": "Do not display the banner"},
    "title": {"type": "bool", "help": "Full title as file name"},
    "quality": {"type": "str", "help": "Specify the movie resolution"},
    "retry": {"type": "str", "help": "Number of retries for downloading segments"},
    "delay": {"type": "str", "help": "Delay in seconds before retry"},
    "timeout": {"type": "str", "help": "Timeout in seconds for segment download"},
}

# 主页面模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Miyuki Downloader</title>
</head>
<body>
    <h1>Miyuki Downloader</h1>
    <form method="post" action="/submit">
        <table border="1">
            <tr>
                <th>Option</th>
                <th>Value</th>
                <th>Description</th>
            </tr>
            {% for key, value in options.items() %}
            <tr>
                <td>-{{ key }}</td>
                <td>
                    {% if value['type'] == 'bool' %}
                    <input type="checkbox" name="{{ key }}">
                    {% elif value['type'] == 'list' %}
                    <input type="text" name="{{ key }}" placeholder="Separate with spaces">
                    {% else %}
                    <input type="text" name="{{ key }}">
                    {% endif %}
                </td>
                <td>{{ value['help'] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

# 提交结果页面模板
RESULT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Miyuki Downloader - Result</title>
</head>
<body>
    <h1>Miyuki Downloader - Result</h1>
    <pre>{{ result }}</pre>
    <br>
    <a href="/">Back to Home</a>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    """显示主页面，提供输入表单"""
    return render_template_string(HTML_TEMPLATE, options=MIYUKI_OPTIONS)


@app.route("/submit", methods=["POST"])
def submit():
    """处理表单提交，运行 miyuki 命令"""
    # 创建一个 argparse.Namespace 对象
    args = argparse.Namespace()

    # 遍历所有选项
    for key, value in MIYUKI_OPTIONS.items():
        if value["type"] == "bool":
            # 如果是布尔类型，检查是否勾选
            setattr(args, key, bool(request.form.get(key)))
        elif value["type"] == "list":
            # 如果是列表类型，获取输入并分割
            input_value = request.form.get(key)
            if input_value:
                setattr(args, key, input_value.split())
            else:
                setattr(args, key, None)
        else:
            # 如果是字符串类型，直接获取输入
            input_value = request.form.get(key)
            if input_value:
                setattr(args, key, input_value)
            else:
                setattr(args, key, None)

    # 调用 miyuki 的 execute_download 函数
    try:
        miyuki.execute_download(args)
        output = "Download completed successfully."
    except Exception as e:
        output = f"Failed to run miyuki command: {e}"

    # 显示结果页面
    return render_template_string(RESULT_TEMPLATE, result=output)


if __name__ == "__main__":
    # 启动 Flask 服务器，监听 9898 端口
    app.run(host="0.0.0.0", port=9898)
