from app.repositories import generate_suggested_reply


def test_generate_suggested_reply_for_finance_high_priority():
    reply = generate_suggested_reply(
        category="FINANCE",
        priority="HIGH",
        assigned_to="finance_priority_team",
    )

    assert "finansów" in reply
    assert "pilna" in reply
    assert "finance_priority_team" in reply


def test_generate_suggested_reply_for_finance_medium_priority():
    reply = generate_suggested_reply(
        category="FINANCE",
        priority="MEDIUM",
        assigned_to="finance_team",
    )

    assert "finansów" in reply
    assert "finance_team" in reply


def test_generate_suggested_reply_for_it_high_priority():
    reply = generate_suggested_reply(
        category="IT_SUPPORT",
        priority="HIGH",
        assigned_to="it_priority_team",
    )

    assert "techniczny" in reply
    assert "pilny" in reply
    assert "it_priority_team" in reply


def test_generate_suggested_reply_for_hr_ticket():
    reply = generate_suggested_reply(
        category="HR",
        priority="MEDIUM",
        assigned_to="hr_team",
    )

    assert "kadrowa" in reply
    assert "hr_team" in reply


def test_generate_suggested_reply_for_other_high_priority():
    reply = generate_suggested_reply(
        category="OTHER",
        priority="HIGH",
        assigned_to="general_priority_team",
    )

    assert "pilna" in reply
    assert "general_priority_team" in reply


def test_generate_suggested_reply_falls_back_when_assignee_missing():
    reply = generate_suggested_reply(
        category="OTHER",
        priority="LOW",
        assigned_to=None,
    )

    assert "odpowiedni zespół" in reply