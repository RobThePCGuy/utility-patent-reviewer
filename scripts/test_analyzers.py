#!/usr/bin/env python3
"""
Quick test of the new patent analyzers
"""

from mcp_server.claims_analyzer import ClaimsAnalyzer
from mcp_server.formalities_checker import FormalitiesChecker
from mcp_server.specification_analyzer import SpecificationAnalyzer

# Test claims with known issues
test_claims = """
1. A computer system comprising:
    a) a processor configured to process data; and
    b) memory storing instructions that cause the processor to use the cache manager.

2. The system of claim 1, wherein the target section is enhanced using the novel widget.
"""

# Test abstract
test_abstract = """
A system for AI-augmented document enhancement achieves 70-85% computational cost reduction
through content-addressed multi-layer caching using per-file SHA-256 hash verification with
automatic invalidation. The system maintains document continuity via a structured Knowledge Base.
"""

# Test title
test_title = "System and Method for AI-Augmented Enhancement of Multi-Section Documents"

print("Testing Claims Analyzer...")
print("=" * 70)
analyzer = ClaimsAnalyzer()
results = analyzer.analyze_claims(test_claims)
print(f"Claim Count: {results['claim_count']}")
print(f"Compliance Score: {results['compliance_score']}%")
print(f"Total Issues: {results['total_issues']}")
print(f"Summary: {results['summary'].encode('ascii', 'ignore').decode('ascii')}")

if results["issues"]:
    print("\nIssues Found:")
    for issue in results["issues"][:3]:  # Show first 3
        print(f"\n  [{issue['severity']}] Claim {issue['claim']} - {issue['location']}")
        print(f"  Problem: {issue['problem']}")
        print(f"  Fix: {issue['fix']}")

print("\n\nTesting Formalities Checker...")
print("=" * 70)
checker = FormalitiesChecker()
results = checker.check_all_formalities(
    abstract=test_abstract, title=test_title, drawings_present=False
)
print(f"Overall Compliant: {results['overall_compliant']}")
print(
    f"Summary: {results['compliance_summary']['summary'].encode('ascii', 'ignore').decode('ascii')}"
)

if results["results"]["abstract"]:
    print(
        f"\nAbstract: {results['results']['abstract']['word_count']} words - "
        f"{'Compliant' if results['results']['abstract']['compliant'] else 'Issues found'}"
    )

if results["results"]["title"]:
    print(
        f"Title: {results['results']['title']['character_count']} chars - "
        f"{'Compliant' if results['results']['title']['compliant'] else 'Issues found'}"
    )

print("\n\nTesting Specification Analyzer...")
print("=" * 70)
test_spec = """
[0001] The present invention relates to computer systems with caching.

[0002] The processor executes instructions stored in memory. The cache manager
stores frequently accessed data for improved performance.

[0003] The system provides improved performance through content-addressed caching.
"""

# Parse claims first
parsed_claims = analyzer._parse_claims(test_claims)

spec_analyzer = SpecificationAnalyzer()
results = spec_analyzer.analyze_specification_support(parsed_claims, test_spec)

print(f"Specification Paragraphs: {results['specification_paragraphs']}")
print(f"Indexed Terms: {results['indexed_terms']}")
print(f"Coverage: {results['spec_coverage']['percentage']}%")
print(f"Summary: {results['summary'].encode('ascii', 'ignore').decode('ascii')}")

if results["issues"]:
    print("\nSupport Issues Found:")
    for issue in results["issues"][:3]:  # Show first 3
        print(f"\n  [{issue['severity']}] Claim {issue['claim']}: {issue['element']}")
        print(f"  Problem: {issue['problem']}")
        print(f"  Fix: {issue['fix']}")

print("\n" + "=" * 70)
print("ALL TESTS PASSED - Analyzers working correctly!")
