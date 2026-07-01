#!/usr/bin/env python3
"""读取 data.txt，生成 GitHub 风格的 consume graph HTML 页面。"""

from datetime import datetime, timedelta
from html import escape

# 0 = empty (gray), 1-8 = 8 levels of green
LEVEL_COLORS = [
    "#ebedf0",  # 0 - no consumes
    "#9be9a8",  # 1 - lightest green
    "#8ad798",  # 2
    "#78c688",  # 3
    "#67b478",  # 4
    "#56a368",  # 5
    "#449158",  # 6
    "#338048",  # 7
    "#216e39",  # 8 - darkest green
]


def parse_data(filepath):
    consumes = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            dt = datetime.strptime(line, "%H:%M:%S %d/%m/%y")
            dt_utc8 = dt + timedelta(hours=8)
            consumes.append(dt_utc8)
    return consumes


def is_dead_range(hour, day):
    """Check if a (hour, day-of-June) cell falls in Jun 12 17:00 ~ Jun 13 15:00."""
    if day == 12 and 17 <= hour <= 23:
        return True
    if day == 13 and 0 <= hour <= 15:
        return True
    return False


def main():
    consumes = parse_data("data.txt")
    num_days = 30

    # Grid stores consume counts per hour per day
    grid = [[0] * num_days for _ in range(24)]

    for c in consumes:
        if c.month == 5 and c.day == 31:
            d = 29  # Map May 31 to June 30
        elif c.month == 6 and 1 <= c.day <= 30:
            d = c.day - 1
        elif c.month == 7 and c.day == 1:
            d = 0
        else:
            continue
        grid[c.hour][d] += 1

    hourly_counts = [sum(grid[h]) for h in range(24)]
    total = sum(hourly_counts)

    show_dates = {0: "6/1", 4: "6/5", 9: "6/10", 14: "6/15", 19: "6/20", 24: "6/25", 29: "6/30"}

    h = []
    h.append("<!DOCTYPE html>")
    h.append('<html lang="en">')
    h.append("<head>")
    h.append('<meta charset="utf-8">')
    h.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    h.append("<title>Consumption Graph</title>")
    h.append("<style>")
    h.append("""*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:#f6f8fa;color:#1f2328;padding:20px 10px;display:flex;justify-content:center}
.card{background:#fff;border:1px solid #d0d7de;border-radius:6px;padding:12px;max-width:720px;width:100%}
.header{margin-bottom:10px}
.header h2{font-size:13px;font-weight:600;margin-bottom:1px}
.subtitle{font-size:11px;color:#656d76}
.graph-scroll{overflow-x:auto}
.date-row{display:flex;align-items:flex-end;height:12px;margin-bottom:3px;font-size:9px;color:#656d76;white-space:nowrap}
.hour-spacer{width:32px;flex-shrink:0}
.days-wrap{display:flex;gap:1px;flex-shrink:0}
.day-l{width:10px;height:10px;display:inline-block;text-align:left;font-size:8px;line-height:10px;overflow:visible;white-space:nowrap}
.gap-spacer{width:6px;flex-shrink:0}
.sum-spacer{width:10px;flex-shrink:0}
.num-spacer{width:18px;flex-shrink:0}
table.graph{table-layout:fixed;border-collapse:separate;border-spacing:1px}
th,td{font-size:9px;color:#656d76;overflow:visible}
.col-hour{width:32px}
.col-day{width:10px}
.col-gap{width:6px}
.col-sum{width:10px}
.col-num{width:18px}
th.date-h{height:12px;text-align:left;font-weight:400;white-space:nowrap}
td.hour-l{text-align:left;font-size:8px;white-space:nowrap;padding:0 4px 0 0;line-height:10px;vertical-align:middle}
td.cell-w{width:10px;height:10px;text-align:center;vertical-align:middle;padding:0}
.cell{width:9px;height:9px;border-radius:2px;display:inline-block}
td.skull{width:10px;height:10px;font-size:9px;line-height:10px;text-align:center;vertical-align:middle;padding:0;overflow:visible}
td.sum-num{font-size:9px;color:#656d76;padding-left:2px;white-space:nowrap;line-height:10px;vertical-align:middle;text-align:left}
th.sum-h{text-align:left;font-weight:400;font-size:9px;padding-left:2px;white-space:nowrap}
.legend{margin-top:8px;display:flex;align-items:center;gap:2px;font-size:10px;color:#656d76;justify-content:flex-end}""")
    h.append("</style>")
    h.append("</head>")
    h.append("<body>")
    h.append('<div class="card">')
    h.append('<div class="header">')
    h.append("<h2>Consumption Graph</h2>")
    h.append(f'<p class="subtitle">{total} Xanax consumed · June 2026</p>')
    h.append("</div>")
    h.append('<div class="graph-scroll">')

    # Date row: hour spacer + day labels + gap + sum + num
    h.append('<div class="date-row">')
    h.append('<span class="hour-spacer"></span>')
    h.append('<span class="days-wrap">')
    for d in range(num_days):
        label = show_dates.get(d, "")
        h.append(f'<span class="day-l">{escape(label)}</span>')
    h.append('</span>')
    h.append('<span class="gap-spacer"></span>')
    h.append('<span class="sum-spacer"></span>')
    h.append('<span class="num-spacer"></span>')
    h.append('</div>')

    h.append('<table class="graph">')

    # colgroup: hour, days, gap, sum, num
    h.append("<colgroup>")
    h.append('<col class="col-hour">')
    for _ in range(num_days):
        h.append('<col class="col-day">')
    h.append('<col class="col-gap">')
    h.append('<col class="col-sum">')
    h.append('<col class="col-num">')
    h.append("</colgroup>")

    # 24 rows: hour label on the left, then day cells, then summary
    for hr in range(24):
        h.append("<tr>")
        # Hour label (left-aligned, every 3 hours)
        if hr % 3 == 0:
            h.append(f'<td class="hour-l">{hr:02d}:00</td>')
        else:
            h.append('<td class="hour-l"></td>')
        # Day cells
        for d in range(num_days):
            day_num = d + 1
            in_dead = is_dead_range(hr, day_num)
            if in_dead:
                h.append('<td class="skull">💀</td>')
            else:
                count = grid[hr][d]
                if count > 0:
                    level = min(count, 8)
                    color = LEVEL_COLORS[level]
                    title = f"{count} at {hr:02d}:00 on Jun {day_num}"
                    h.append(f'<td class="cell-w"><span class="cell" style="background:{color}" title="{escape(title)}"></span></td>')
                else:
                    h.append(f'<td class="cell-w"><span class="cell" style="background:{LEVEL_COLORS[0]}"></span></td>')
        # Gap
        h.append('<td class="cell-w"></td>')
        # Summary cell
        count = hourly_counts[hr]
        level = min(count, 8)
        h.append(f'<td class="cell-w"><span class="cell" style="background:{LEVEL_COLORS[level]}" title="{count} Xanax consumed"></span></td>')
        # Count number
        h.append(f'<td class="sum-num">{count}</td>')
        h.append("</tr>")

    h.append("</table>")
    h.append("</div>")

    # Legend
    h.append('<div class="legend">')
    h.append("<span>Less</span>")
    for i in range(9):
        h.append(f'<span class="cell" style="background:{LEVEL_COLORS[i]}"></span>')
    h.append("<span>More</span>")
    h.append("</div>")

    h.append("</div>")
    h.append("</body>")
    h.append("</html>")

    out = "consume_graph.html"
    with open(out, "w") as f:
        f.write("\n".join(h))
    print(f"Saved {out} ({total} consumes shown)")


if __name__ == "__main__":
    main()
