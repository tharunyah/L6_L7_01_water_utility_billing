"""
Student Name: Tharunyah Sudhakar
SRN: PES2UG24CS561
Section: J
Lab 6: Branch Coverage Test Cases for Water Utility Billing
"""

import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


# =====================================================================
# Branch Coverage Tests for calculate_water_bill
# =====================================================================

def test_branch_invalid_accounts_not_a_list():
    """Branch 1A: accounts is not a list -> raises ValueError."""
    with pytest.raises(ValueError, match="Invalid accounts list or base fee"):
        calculate_water_bill("not_a_list", 10.0)


def test_branch_invalid_base_fee_negative():
    """Branch 1B: base_fee < 0 -> raises ValueError."""
    with pytest.raises(ValueError, match="Invalid accounts list or base fee"):
        calculate_water_bill([], -1.0)


def test_branch_accounts_empty_no_activity():
    """Branch 2A: accounts loop doesn't execute; total_billed == 0.0 -> NO_ACTIVITY."""
    result = calculate_water_bill([], 0.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_branch_account_inactive():
    """Branch 3A: not account.get('is_active') is True -> continue to next account."""
    accounts = [
        {"is_active": False, "usage_blocks": [50]}
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_branch_account_empty_usage_blocks():
    """Branch 4A: account is active but usage_blocks is empty -> acct_total = base_fee."""
    accounts = [
        {"is_active": True, "usage_blocks": []}
    ]
    result = calculate_water_bill(accounts, 15.0)
    assert result["total_billed"] == 15.0
    assert result["status"] == "NORMAL"


def test_branch_usage_less_than_equal_zero():
    """Branch 5A: usage <= 0 -> flagged_accounts += 1 and continue."""
    accounts = [
        {"is_active": True, "usage_blocks": [0, -10]}
    ]
    result = calculate_water_bill(accounts, 20.0)
    assert result["total_billed"] == 20.0
    assert result["status"] == "NORMAL"


def test_branch_usage_tier_low():
    """Branch 6A: 0 < usage <= 50 -> rate 1.5."""
    accounts = [
        {"is_active": True, "is_commercial": False, "usage_blocks": [50]}
    ]
    # 10 + 50 * 1.5 = 85.0
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 85.0
    assert result["status"] == "NORMAL"


def test_branch_usage_tier_mid():
    """Branch 6B: 50 < usage <= 100 -> rate 2.5."""
    accounts = [
        {"is_active": True, "is_commercial": False, "usage_blocks": [100]}
    ]
    # 10 + 100 * 2.5 = 260.0
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 260.0
    assert result["status"] == "NORMAL"


def test_branch_usage_tier_high_residential_with_break():
    """Branch 6C: usage > 100 and residential (not is_commercial) -> rate 4.5 and BREAK."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "usage_blocks": [105, 30]  # 30 is unreachable due to break
        }
    ]
    # 10 + 105 * 4.5 = 482.5
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 482.5
    assert result["status"] == "NORMAL"


def test_branch_usage_tier_high_commercial_no_break():
    """Branch 6D: usage > 100 and commercial (is_commercial) -> rate 3.5 without break."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": True,
            "usage_blocks": [110, 40]  # Both processed: 110*3.5 + 40*1.5
        }
    ]
    # 10 + 385 + 60 = 455.0
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 455.0
    assert result["status"] == "NORMAL"


def test_branch_leak_waiver_applied():
    """Branch 7A: has_leak_waiver True AND acct_total > 200.0 -> deduct 50.0."""
    accounts = [
        {
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [80]  # 10 + 80 * 2.5 = 210.0 > 200 -> 210 - 50 = 160.0
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 160.0
    assert result["status"] == "NORMAL"


def test_branch_leak_waiver_not_applied_low_total():
    """Branch 7B: has_leak_waiver True but acct_total <= 200.0 -> no deduction."""
    accounts = [
        {
            "is_active": True,
            "has_leak_waiver": True,
            "usage_blocks": [40]  # 10 + 40 * 1.5 = 70.0 <= 200 -> no deduction
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 70.0
    assert result["status"] == "NORMAL"


def test_branch_leak_waiver_false():
    """Branch 7C: has_leak_waiver False -> no waiver branch executed."""
    accounts = [
        {
            "is_active": True,
            "has_leak_waiver": False,
            "usage_blocks": [80]  # 10 + 80 * 2.5 = 210.0, no deduction
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 210.0
    assert result["status"] == "NORMAL"


def test_branch_status_excessive_flags():
    """Branch 8A: flagged_accounts > 5 -> status EXCESSIVE_FLAGS."""
    accounts = [
        {
            "is_active": True,
            "usage_blocks": [-1, -2, -3, -4, -5, -6]
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_branch_status_normal_with_flags_le_5():
    """Branch 8B: flagged_accounts <= 5 and total_billed > 0 -> status NORMAL."""
    accounts = [
        {
            "is_active": True,
            "usage_blocks": [-1, -2, 20]  # 2 flags <= 5
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["status"] == "NORMAL"


# =====================================================================
# Branch Coverage Tests for check_meter_tampering
# =====================================================================

def test_branch_meter_no_data():
    """Branch 9A: not readings_matrix is True -> return NO_DATA."""
    assert check_meter_tampering([]) == "NO_DATA"
    assert check_meter_tampering(None) == "NO_DATA"


def test_branch_meter_tamper_suspected():
    """Branch 10A: backward_flow_count reaches >= 2 -> TAMPER_SUSPECTED."""
    readings = [
        [5, -2, -4, 10]
    ]
    assert check_meter_tampering(readings) == "TAMPER_SUSPECTED"


def test_branch_meter_single_negative_reset_clear():
    """Branch 10B: backward_flow_count is 1 (delta < 0), then delta >= 0 resets count to 0 -> CLEAR."""
    readings = [
        [-3, 10, -2, 5]
    ]
    assert check_meter_tampering(readings) == "CLEAR"


def test_branch_meter_all_positive_clear():
    """Branch 10C: all delta >= 0 -> CLEAR."""
    readings = [
        [10, 20, 30]
    ]
    assert check_meter_tampering(readings) == "CLEAR"
