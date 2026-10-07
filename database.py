from pathlib import Path

from app.db_access import MERIDIAN_DB, initialize_database
from app.logging_config import get_logger, trace
from db.seed_data import (
    CUSTOMERS, ACCOUNTS, TRANSACTIONS, POLICIES, CLAIMS,
    PORTFOLIOS, INVESTMENT_PRODUCTS, INTERACTIONS, ESCALATIONS, AUDITS,
)

logger = get_logger(__name__)
BASE_DIR = Path(__file__).resolve().parent


@trace(logger)
def _schema():
    return (BASE_DIR / "db" / "schema.sql").read_text(encoding="utf-8")


@trace(logger)
def seed_all(db_path=None):
    initialize_database(
        db_path or MERIDIAN_DB,
        _schema(),
        [
            ("customers", ["customer_id", "full_name", "email", "phone", "customer_tier", "kyc_status", "kyc_last_checked_at", "created_at"], CUSTOMERS),
            ("accounts", ["account_id", "customer_id", "account_type", "balance_cents", "currency", "status", "auto_debit_allowed", "opened_at"], ACCOUNTS),
            ("transactions", ["transaction_id", "account_id", "amount_cents", "direction", "description", "occurred_at"], TRANSACTIONS),
            ("policies", ["policy_id", "customer_id", "policy_type", "premium_cents", "payment_frequency", "payment_terms", "auto_debit_permitted", "status", "coverage_clauses_json", "started_at"], POLICIES),
            ("claims", ["claim_id", "policy_id", "status", "filed_at", "last_updated_at"], CLAIMS),
            ("portfolios", ["portfolio_id", "customer_id", "risk_profile", "total_value_cents", "status", "opened_at"], PORTFOLIOS),
            ("investment_products", ["product_id", "name", "product_type", "min_risk_profile", "description"], INVESTMENT_PRODUCTS),
            ("interaction_log", ["customer_id", "request_id", "channel", "summary", "created_at"], INTERACTIONS),
            ("escalation_flags", ["customer_id", "request_id", "escalation_category", "draft_confidence", "reason", "resolved", "created_at"], ESCALATIONS),
            ("audit_log", ["timestamp", "action_type", "performed_by", "customer_id", "outcome", "detail"], AUDITS),
        ],
    )


@trace(logger)
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true")
    parser.add_argument("--db-path", default=str(MERIDIAN_DB))
    args = parser.parse_args()

    if args.seed:
        db_path = Path(args.db_path)
        seed_all(db_path)
        print(f"Seeded database: {db_path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
