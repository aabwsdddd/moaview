from __future__ import annotations

import re
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "supabase" / "migrations" / "202605090001_initial_schema.sql"
SEED_PATH = Path(__file__).resolve().parents[2] / "supabase" / "seed.sql"

REQUIRED_TABLES = {
    "users_profile",
    "works",
    "creators",
    "work_creators",
    "platforms",
    "platform_works",
    "offers",
    "promotions",
    "coupons",
    "computed_offer_prices",
    "favorites",
    "notification_rules",
    "notification_events",
    "search_events",
    "detail_view_events",
    "click_events",
    "price_history",
    "crawl_logs",
    "raw_platform_data",
    "merge_review_queue",
}


def schema_sql() -> str:
    return SCHEMA_PATH.read_text(encoding="utf-8")


def table_block(sql: str, table_name: str) -> str:
    match = re.search(rf"create table {table_name} \((.*?)\n\);", sql, flags=re.S)
    assert match, f"Missing create table block for {table_name}"
    return match.group(1)


def assert_columns(table_name: str, columns: set[str]) -> None:
    block = table_block(schema_sql(), table_name)
    for column in columns:
        assert re.search(rf"^\s*{column}\b", block, flags=re.M), f"{table_name}.{column} is missing"


def test_required_tables_exist() -> None:
    sql = schema_sql()
    for table_name in REQUIRED_TABLES:
        assert f"create table {table_name}" in sql


def test_content_type_supports_webtoon_and_webnovel() -> None:
    sql = schema_sql()
    assert "create type content_type as enum ('WEBTOON', 'WEBNOVEL')" in sql
    assert_columns("works", {"content_type"})


def test_offers_keep_source_and_last_updated_metadata() -> None:
    assert_columns("offers", {"source_url", "source_type", "last_updated_at"})


def test_promotions_support_required_promotion_types() -> None:
    sql = schema_sql()
    for promotion_type in [
        "instant_discount",
        "cashback",
        "bonus_currency",
        "free_episode_event",
        "bundle_discount",
    ]:
        assert f"'{promotion_type}'" in sql
    assert_columns("promotions", {"promotion_type"})


def test_coupons_support_required_issuance_flags() -> None:
    assert_columns(
        "coupons",
        {
            "downloadable",
            "auto_issued",
            "code_required",
            "first_purchase_only",
            "user_targeted",
            "min_purchase_amount",
            "max_discount_amount",
        },
    )


def test_computed_offer_prices_store_required_price_fields() -> None:
    assert_columns(
        "computed_offer_prices",
        {
            "base_price",
            "instant_discounted_price",
            "coupon_expected_price",
            "cashback_adjusted_price",
            "effective_price_for_sort",
            "price_confidence",
            "calculation_note",
            "applied_promotion_ids",
            "applied_coupon_ids",
            "calculated_at",
        },
    )


def test_event_tables_support_anonymous_identity_and_click_context() -> None:
    assert_columns("search_events", {"user_id", "anonymous_session_id", "query", "result_count", "created_at"})
    assert_columns("detail_view_events", {"user_id", "anonymous_session_id", "work_id", "created_at"})
    assert_columns(
        "click_events",
        {
            "user_id",
            "anonymous_session_id",
            "work_id",
            "offer_id",
            "platform_id",
            "cta_type",
            "effective_price_at_click",
            "destination_url",
            "created_at",
        },
    )
    assert_columns("notification_events", {"user_id", "anonymous_session_id", "event_type", "payload", "created_at"})


def test_seed_file_contains_small_fixture_structure() -> None:
    seed_sql = SEED_PATH.read_text(encoding="utf-8")
    assert "insert into platforms" in seed_sql
    assert "insert into works" in seed_sql
    assert "insert into offers" in seed_sql
    assert "work_moonlight_archive" in seed_sql
    assert "work_clockwork_palace" in seed_sql
