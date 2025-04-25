from typing import Dict, Any, List

def format_receipt(data: Dict[str, Any], width: int = 40) -> str:
    lines: List[str] = []
    center = lambda s: s.center(width)

    lines.append(center("=== ЧЕК ==="))
    for item in data["products"]:
        name = item["name"]
        qty = f"{item['quantity']:.2f}"
        price = f"{item['price']:.2f}"
        total = f"{item['total']:.2f}"
        lines.append(f"{qty} x {price}".rjust(width))
        lines.append(f"{name} {total}".ljust(width))
        lines.append("-" * width)
    lines.append(f"СУМА: {data['total']:.2f}".rjust(width))
    lines.append(f"{data['payment']['type'].value.capitalize()}: {data['payment']['amount']:.2f}".rjust(width))
    lines.append(f"Решта: {data['rest']:.2f}".rjust(width))
    lines.append("=" * width)
    dt = data["created_at"].strftime("%d.%m.%Y %H:%M")
    lines.append(center(dt))
    lines.append(center("Дякуємо за покупку!"))
    return "\n".join(lines)
