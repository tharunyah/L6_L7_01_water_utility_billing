"""
Student Name: Tharunyah Sudhakar
SRN: PES2UG24CS561
Section: J
Lab 6: Code Coverage Test Cases for Water Utility Billing
"""

import pytest
from water_utility_billing import calculate_water_bill, check_meter_tampering


# =====================================================================
# Tests for calculate_water_bill
# =====================================================================

def test_invalid_accounts_type():
    """Test when accounts is not a list; should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid accounts list or base fee"):
        calculate_water_bill("invalid_type", 10.0)


def test_negative_base_fee():
    """Test when base_fee is negative; should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid accounts list or base fee"):
        calculate_water_bill([], -5.0)


def test_empty_accounts_list():
    """Test when accounts list is empty; should return 0.0 and NO_ACTIVITY."""
    result = calculate_water_bill([], 0.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_inactive_account_skipped():
    """Test that inactive accounts are skipped without processing."""
    accounts = [
        {
            "is_active": False,
            "usage_blocks": [30, 60]
        }
    ]
    result = calculate_water_bill(accounts, 15.0)
    assert result["total_billed"] == 0.0
    assert result["status"] == "NO_ACTIVITY"


def test_non_positive_usage_blocks():
    """Test non-positive usage blocks (<= 0) flagging and continuing."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [0, -15, 20]
        }
    ]
    # base_fee: 10.0, 20 * 1.5 = 30.0 -> total = 40.0, flagged = 2
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 40.0
    assert result["status"] == "NORMAL"


def test_residential_usage_tier_low():
    """Test residential low tier (<= 50) usage block."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [30]
        }
    ]
    # base_fee: 10.0, 30 * 1.5 = 45.0 -> total = 55.0
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 55.0
    assert result["status"] == "NORMAL"


def test_residential_usage_tier_mid():
    """Test mid tier (50 < usage <= 100) usage block."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [70]
        }
    ]
    # base_fee: 10.0, 70 * 2.5 = 175.0 -> total = 185.0
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 185.0
    assert result["status"] == "NORMAL"


def test_residential_high_usage_with_break():
    """Test residential high tier (> 100) usage block triggers 4.5 multiplier and breaks loop."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [120, 30]  # 30 should not be reached because of break
        }
    ]
    # base_fee: 10.0, 120 * 4.5 = 540.0 -> total = 550.0, flagged = 1
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 550.0
    assert result["status"] == "NORMAL"


def test_commercial_high_usage_no_break():
    """Test commercial high tier (> 100) usage block triggers 3.5 multiplier without break."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": True,
            "has_leak_waiver": False,
            "usage_blocks": [110, 40]  # Both blocks are processed
        }
    ]
    # base_fee: 10.0, 110 * 3.5 = 385.0, 40 * 1.5 = 60.0 -> total = 455.0, flagged = 1
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 455.0
    assert result["status"] == "NORMAL"


def test_leak_waiver_applied_when_above_threshold():
    """Test leak waiver deduction (-$50) when acct_total exceeds $200."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": True,
            "usage_blocks": [90]  # 10 + 90 * 2.5 = 235.0 > 200 -> 235.0 - 50.0 = 185.0
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 185.0
    assert result["status"] == "NORMAL"


def test_leak_waiver_not_applied_when_below_threshold():
    """Test leak waiver is NOT deducted when acct_total does not exceed $200."""
    accounts = [
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": True,
            "usage_blocks": [40]  # 10 + 40 * 1.5 = 70.0 <= 200 -> no deduction
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["total_billed"] == 70.0
    assert result["status"] == "NORMAL"


def test_excessive_flags_status():
    """Test excessive flagged accounts status (> 5 flagged events)."""
    accounts = [
        {
            "is_active": True,
            "usage_blocks": [-1, -2, -3, -4, -5, -6]  # 6 non-positive blocks -> 6 flags
        }
    ]
    result = calculate_water_bill(accounts, 10.0)
    assert result["status"] == "EXCESSIVE_FLAGS"


def test_multiple_accounts_aggregate():
    """Test processing multiple accounts together."""
    accounts = [
        {
            "is_active": False,
            "usage_blocks": [100]
        },
        {
            "is_active": True,
            "is_commercial": False,
            "has_leak_waiver": False,
            "usage_blocks": [20]  # 5 + 30 = 35
        },
        {
            "is_active": True,
            "is_commercial": True,
            "has_leak_waiver": True,
            "usage_blocks": [150]  # 5 + 150*3.5 = 530 - 50 = 480
        }
    ]
    result = calculate_water_bill(accounts, 5.0)
    assert result["total_billed"] == 515.0
    assert result["status"] == "NORMAL"


# =====================================================================
# Tests for check_meter_tampering
# =====================================================================

def test_tampering_no_data():
    """Test empty readings matrix returns NO_DATA."""
    assert check_meter_tampering([]) == "NO_DATA"
    assert check_meter_tampering(None) == "NO_DATA"


def test_tampering_suspected_consecutive_negatives():
    """Test tamper suspected when backward flow count reaches 2 consecutive negatives."""
    readings = [
        [10, -5, -3, 8]
    ]
    assert check_meter_tampering(readings) == "TAMPER_SUSPECTED"


def test_tampering_clear_with_reset():
    """Test backward flow counter resets to 0 upon positive flow, clearing tampering."""
    readings = [
        [-5, 10, -3, 8, -2, 5]
    ]
    assert check_meter_tampering(readings) == "CLEAR"


def test_tampering_clear_multiple_meters():
    """Test multiple meters all clearing with no tampering."""
    readings = [
        [1, 2, 3],
        [4, -1, 5, 6],
        [7, 8, 9]
    ]
    assert check_meter_tampering(readings) == "CLEAR"
