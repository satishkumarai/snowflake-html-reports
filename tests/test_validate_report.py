from pathlib import Path

from scripts.validate_report import main, validate

GOOD = """<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script type="application/json" id="snowflake-report-metadata">
{"sections":[{"id":"s1","title":"S1"}]}
</script></head><body><h2 id="s1">S1</h2>
<script src="/libs/chart.js@4.4.4/chart.umd.js"></script>
<script>document.getElementById('s1').addEventListener('click', function(){});</script>
</body></html>"""


def rules(html):
    return {f.rule for f in validate(html)}


def test_clean_report_passes():
    assert not [f for f in validate(GOOD) if f.level == "error"]


def test_inline_handler_blocked():
    assert "inline-event-handler" in rules(GOOD.replace("<h2 id", '<h2 onclick="x()" id'))


def test_cdn_script_blocked():
    bad = GOOD.replace("/libs/chart.js@4.4.4/chart.umd.js", "https://cdn.jsdelivr.net/chart.js")
    assert "external-script" in rules(bad)


def test_network_call_blocked():
    assert "network-call" in rules(GOOD.replace("function(){}", "function(){fetch('/x')}"))


def test_missing_metadata():
    assert "missing-metadata" in rules("<html><body>x</body></html>")


def test_orphan_section():
    assert "orphan-section" in rules(GOOD.replace('<h2 id="s1">', "<h2>"))


def test_placeholder_left():
    assert "placeholder-left" in rules(GOOD.replace('"S1"', '"{DATABASE}"'))


def test_sensitive_column_warns():
    f = [x for x in validate(GOOD + "<td>email</td>") if x.rule == "sensitive-column"]
    assert f and f[0].level == "warn"


def test_size_budget():
    assert "file-size" in {f.rule for f in validate(GOOD, max_bytes=10)}


def test_cli_exit_codes(tmp_path: Path):
    ok = tmp_path / "ok.html"
    ok.write_text(GOOD)
    bad = tmp_path / "bad.html"
    bad.write_text("<html></html>")
    assert main([str(ok)]) == 0
    assert main([str(bad)]) == 1


def test_sample_report_passes():
    sample = Path(__file__).parents[1] / "reports/finops-credits/report.html"
    assert main([str(sample), "--strict"]) == 0
