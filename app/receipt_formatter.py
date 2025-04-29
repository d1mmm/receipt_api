from typing import Dict, Any
from jinja2 import Template

_receipt_template = Template(r"""
{{ "=== RECEIPT ===".center(width) }}
{% for item in products %}
{{ ("%0.2f x %0.2f" % (item.quantity, item.price)).rjust(width) }}
{{ (item.name + "  " + "%0.2f" % item.total).ljust(width) }}
{{ "-" * width }}
{% endfor %}
{{ ("TOTAL: " + "%0.2f" % total).rjust(width) }}
{{ ("Payment (" + payment.type.capitalize() + "): " + "%0.2f" % payment.amount).rjust(width) }}
{{ ("CHANGE: " + "%0.2f" % rest).rjust(width) }}
{{ "=" * width }}
{{ created_at.strftime("%Y-%m-%d %H:%M").center(width) }}
{{ "Thank you for your purchase!".center(width) }}
""")

def format_receipt(data: Dict[str, Any], width: int = 40) -> str:
    return _receipt_template.render(
        products=data["products"],
        payment=data["payment"],
        total=data["total"],
        rest=data["rest"],
        created_at=data["created_at"],
        width=width
    )
