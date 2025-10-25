from pathlib import Path

from spooky.config_models import KarmaConfig
from spooky.karma import KarmaManager


def build_config(tmp_path: Path) -> KarmaConfig:
    return KarmaConfig(
        thresholds={"novice": 0, "specialist": 10},
        default_role="novice",
        storage_path=tmp_path / "karma_state.json",
    )


def test_award_promotes_to_specialist(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    manager = KarmaManager(config)

    profile = manager.award("alice", 5)
    assert profile.karma == 5
    assert profile.role == "novice"

    profile = manager.award("alice", 5)
    assert profile.karma == 10
    assert profile.role == "specialist"

    persisted_manager = KarmaManager(config)
    persisted_profile = persisted_manager.get_profile("alice")
    assert persisted_profile.karma == 10
    assert persisted_profile.role == "specialist"


def test_award_handles_negative_points(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    manager = KarmaManager(config)

    manager.award("bob", 8)
    profile = manager.award("bob", -20)
    assert profile.karma == 0
    assert profile.role == "novice"


def test_leaderboard_sorting(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    manager = KarmaManager(config)

    manager.award("charlie", 4)
    manager.award("dana", 7)
    manager.award("charlie", 7)  # total 11

    leaderboard = manager.list_profiles()
    assert [profile.username for profile in leaderboard] == ["charlie", "dana"]
    assert leaderboard[0].role == "specialist"
