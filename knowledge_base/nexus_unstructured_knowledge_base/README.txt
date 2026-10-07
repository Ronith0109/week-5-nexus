NEXUS — UNSTRUCTURED KNOWLEDGE BASE

This package contains 64 substantial TXT documents for the Nexus hybrid-RAG demonstration.

The knowledge base covers:
- Banking policies
- Insurance policies and claims
- Wealth policies
- All 10 structured investment products
- Banking, insurance, and wealth FAQs
- Cross-product banking/insurance rules
- Regulatory and governance notes
- Customer communication templates
- Adversarial retrieval/test documents

IMPORTANT STRUCTURED-DATA BOUNDARY
General knowledge in these documents does not replace live MCP data for customer-specific facts.

SHOWCASE ALIGNMENT
CUS-20077 / Arjun Mehta has ACC-20077, which is a CHECKING account, active, with auto_debit_allowed=1.
POL-IN-30091 is an ACTIVE HEALTH policy with auto-debit permitted and monthly payment terms.
The package intentionally preserves this exact structured fact.

CONFLICT TEST
CUS-30142 has POL-GE-30250 with policy-level auto-debit permission, while ACC-30142 is restricted
and has auto_debit_allowed=0. This is intentionally included for retrieval-conflict testing.

SIZING
Every knowledge TXT is generated as a substantial multi-section document intended to exceed roughly
three pages under ordinary text-document formatting. Exact page count depends on font, margins,
line spacing, and viewer.

PACKAGE CONTENTS
64 TXT knowledge documents
1 README.txt
1 MANIFEST.csv
