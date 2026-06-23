from app.repositories import determine_default_assignee


def test_determine_default_assignee_for_finance_high_priority():
    assignee = determine_default_assignee(
        category="FINANCE",
        priority="HIGH",
    )

    assert assignee == "finance_priority_team"


def test_determine_default_assignee_for_finance_medium_priority():
    assignee = determine_default_assignee(
        category="FINANCE",
        priority="MEDIUM",
    )

    assert assignee == "finance_team"


def test_determine_default_assignee_for_it_high_priority():
    assignee = determine_default_assignee(
        category="IT_SUPPORT",
        priority="HIGH",
    )

    assert assignee == "it_priority_team"


def test_determine_default_assignee_for_it_low_priority():
    assignee = determine_default_assignee(
        category="IT_SUPPORT",
        priority="LOW",
    )

    assert assignee == "it_support_team"


def test_determine_default_assignee_for_hr_high_priority():
    assignee = determine_default_assignee(
        category="HR",
        priority="HIGH",
    )

    assert assignee == "hr_priority_team"


def test_determine_default_assignee_for_hr_medium_priority():
    assignee = determine_default_assignee(
        category="HR",
        priority="MEDIUM",
    )

    assert assignee == "hr_team"


def test_determine_default_assignee_for_other_high_priority():
    assignee = determine_default_assignee(
        category="OTHER",
        priority="HIGH",
    )

    assert assignee == "general_priority_team"


def test_determine_default_assignee_for_other_low_priority():
    assignee = determine_default_assignee(
        category="OTHER",
        priority="LOW",
    )

    assert assignee == "general_team"