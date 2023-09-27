import urllib3
import json
import widgets as wd
from datetime import timedelta
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ZABBIX_URL = "https://your_zabbix_url_here/api_jsonrpc.php"
USER = "login"
PASSWORD = "password"

# Colors
widget_background = [
    wd.Color.rgb(224 / 255, 224 / 255, 224 / 255),
    wd.Color.rgb(230 / 255, 230 / 255, 230 / 255),
]
disaster_background_color = wd.Color.rgb(220 / 255, 71 / 255, 71 / 255)
high_background_color = wd.Color.rgb(220 / 255, 136 / 255, 71 / 255)
warning_background_color = wd.Color.rgb(195 / 255, 195 / 255, 195 / 255)
average_background_color = wd.Color.rgb(233 / 255, 217 / 255, 73 / 255)
metric_box_color = wd.Color.rgb(255 / 255, 255 / 255, 255 / 255)
widget_font_color = wd.Color.rgb(0 / 255, 0 / 255, 0 / 255)

# Sizes
metric_box_padding = 7
metric_box_font_size = 35
metric_box_radius = 10

# Texts
bold_font = "HelveticaNeue-Bold"
regular_font = "HelveticaNeue-Regular"
widget_title = "🚨 ZABBIX"

zabbix_host = urlparse(ZABBIX_URL).netloc


def login_to_zabbix() -> str:
    data_api = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {"user": USER, "password": PASSWORD},
        "id": 1,
    }

    http = urllib3.PoolManager()
    resp = http.request(
        "POST",
        ZABBIX_URL,
        headers={"Content-Type": "application/json"},
        body=json.dumps(data_api),
    )

    try:
        auth_token = json.loads(resp.data.decode("utf-8"))["result"]
    except KeyError:
        print("Unable to login, please check your credentials.")
        auth_token = ""

    return auth_token


def get_opened_problems(auth_token: str) -> dict:
    severity_dict = {
        "0": "not classified",
        "1": "information",
        "2": "warning",
        "3": "average",
        "4": "high",
        "5": "disaster",
    }

    data_api = {
        "jsonrpc": "2.0",
        "method": "problem.get",
        "params": {
            "filter": {"status": "1"},
            "output": "extend",
            "sortfield": ["eventid"],
            "sortorder": "DESC",
        },
        "auth": auth_token,
        "id": 2,
    }

    http = urllib3.PoolManager()
    resp = http.request(
        "POST",
        ZABBIX_URL,
        headers={"Content-Type": "application/json"},
        body=json.dumps(data_api),
    )
    problems = json.loads(resp.data.decode("utf-8"))["result"]
    severity_counts_dict = {
        "not classified": 0,
        "information": 0,
        "warning": 0,
        "average": 0,
        "high": 0,
        "disaster": 0,
    }
    for problem in problems:
        severity_counts_dict[severity_dict[problem["severity"]]] += 1

    print(severity_counts_dict)
    return severity_counts_dict


def result() -> dict:
    opened_problems = {}
    auth_token = login_to_zabbix()
    if auth_token:
        opened_problems = get_opened_problems(auth_token)
    return opened_problems


widget = wd.Widget()

problems = result()

disaster_count = wd.Text(
    str(problems["disaster"]),
    font=wd.Font(bold_font, metric_box_font_size),
    padding=metric_box_padding,
    background_color=disaster_background_color,
    color=metric_box_color,
    corner_radius=metric_box_radius,
)
high_count = wd.Text(
    str(problems["high"]),
    font=wd.Font(bold_font, metric_box_font_size),
    padding=metric_box_padding,
    background_color=high_background_color,
    color=metric_box_color,
    corner_radius=metric_box_radius,
)
average_count = wd.Text(
    str(problems["average"]),
    font=wd.Font(bold_font, metric_box_font_size),
    padding=metric_box_padding,
    background_color=average_background_color,
    color=metric_box_color,
    corner_radius=metric_box_radius,
)
warning_count = wd.Text(
    str(problems["warning"]),
    font=wd.Font(bold_font, metric_box_font_size),
    padding=metric_box_padding,
    background_color=warning_background_color,
    color=metric_box_color,
    corner_radius=metric_box_radius,
)

# Small widget
widget.small_layout.set_background_gradient(colors=widget_background)
widget.small_layout.add_row(
    [
        wd.Text(
            widget_title,
            font=wd.Font(bold_font, 18),
            color=widget_font_color,
        )
    ]
)
widget.small_layout.add_row(
    [
        disaster_count,
    ],
)
widget.small_layout.add_row(
    [
        wd.Text(
            "Host: " + zabbix_host,
            font=wd.Font(regular_font, 11),
            color=widget_font_color,
        ),
    ]
)


# Medium Widget
widget.medium_layout.set_background_gradient(colors=widget_background)
widget.medium_layout.add_row(
    [
        wd.Text(
            widget_title,
            font=wd.Font(bold_font, 18),
            color=widget_font_color,
        ),
        wd.Text(
            "Problems",
            font=wd.Font(regular_font, 18),
            color=widget_font_color,
        ),
    ]
)
widget.medium_layout.add_row(
    [
        disaster_count,
        high_count,
        average_count,
        warning_count,
    ],
)
widget.medium_layout.add_row(
    [
        wd.Text(
            "Host: " + zabbix_host,
            font=wd.Font(regular_font, 11),
            color=widget_font_color,
        ),
    ]
)

# Large Widget
widget.large_layout.set_background_gradient(colors=widget_background)
widget.large_layout.add_row(
    [
        wd.Text(
            widget_title,
            font=wd.Font(bold_font, 18),
            color=widget_font_color,
        ),
        wd.Text(
            "Problems",
            font=wd.Font(regular_font, 18),
            color=widget_font_color,
        ),
    ]
)
widget.large_layout.add_row(
    [
        disaster_count,
        high_count,
    ],
)
widget.large_layout.add_row(
    [
        average_count,
        warning_count,
    ],
)
widget.large_layout.add_row(
    [
        wd.Text(
            "Host: " + zabbix_host,
            font=wd.Font(regular_font, 11),
            color=widget_font_color,
        ),
    ]
)

wd.save_widget(widget, "Zabbix")
wd.schedule_next_reload(timedelta(minutes=1))
wd.show_widget(widget)
