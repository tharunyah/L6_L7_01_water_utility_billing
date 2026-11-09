from hypothesis import given, strategies as st
from processor import sanitize_meter_id, parse_consumption_readings, format_billing_summary

@given(st.text() | st.none())
def test_sanitize_meter_id_no_crash(s):
    # To-Do: Using try and except complete this function.
    try:
        sanitize_meter_id(s)
    except Exception as e:
        assert False, f"sanitize_meter_id crashed with: {e}"

@given(st.text() | st.none())
def test_parse_consumption_readings_safe(s):
    # To-Do: Using try and except complete this function.
    try:
        parse_consumption_readings(s)
    except Exception as e:
        assert False, f"parse_consumption_readings crashed with: {e}"

@given(st.text() | st.none())
def test_format_billing_summary_safe(s):
    # To-Do: Using try and except complete this function.
    try:
        format_billing_summary(s)
    except Exception as e:
        assert False, f"format_billing_summary crashed with: {e}"
