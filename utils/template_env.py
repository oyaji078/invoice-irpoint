from jinja2 import Environment, FileSystemLoader, select_autoescape
from utils.paths import TEMPLATES_DIR


env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(name: str, **context) -> str:
    template = env.get_template(name)
    return template.render(**context)
