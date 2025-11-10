---
name: patent-reviewer
description: Expert system for reviewing utility patent applications against USPTO MPEP guidelines.
---

# Patent Reviewer Skill

Comprehensive patent review system with access to USPTO MPEP, prior art databases, and USPTO API for complete patent application analysis.

## When to Use This Skill

Activate this skill when:
- Reviewing utility patent applications for USPTO compliance
- Analyzing patent claims for 35 USC 112 compliance
- Checking specification requirements (written description, enablement, best mode)
- Verifying formalities (abstract, drawings, title requirements)
- Searching for prior art or similar patents
- Accessing live USPTO patent data
- Preparing applications for USPTO submission

## Available MCP Tools

### MPEP & Statute Search Tools
- `search_mpep(query, top_k, source_filter)` - Search MPEP, 35 USC, 37 CFR sources
- `get_mpep_section(section_number)` - Retrieve specific MPEP section content
- `review_patent_claims(claims_text)` - Automated claims analysis against MPEP
- `review_specification(specification_topic)` - Specification compliance check
- `check_formalities(check_type)` - Verify formality requirements

### USPTO API Tools (Live Data)
- `search_uspto_api(query, grant_from_date, grant_to_date)` - Search live USPTO database
- `get_uspto_patent(patent_number)` - Get specific patent by number
- `get_recent_uspto_patents(days_back)` - Find recently granted patents
- `check_uspto_api_status()` - Verify API connection

### Prior Art Search Tools (Local Corpus - 9.2M+ Patents)
- `search_prior_art(query, top_k, cpc_filter, date_range)` - Semantic prior art search
- `get_patent_details(patent_id)` - Get full patent details by ID
- `check_patent_corpus_status()` - Verify local corpus availability

### Diagram Generation Tools
- `render_diagram(dot_code, output_format)` - Render DOT code to diagram
- `create_flowchart(title, steps)` - Generate flowchart from steps
- `create_block_diagram(title, components)` - Create block diagram
- `add_diagram_references(svg_path, references)` - Add patent-style reference numbers
- `get_diagram_templates()` - Get common diagram templates
- `check_diagram_tools_status()` - Verify Graphviz installation

## Comprehensive Review Process

### Phase 1: Initial Assessment
1. Ask user which sections need review:
   - Complete application
   - Claims only
   - Specification only
   - Formalities only
   - Prior art search
   - Specific concerns

2. Gather required materials:
   - Claims (independent and dependent)
   - Specification (or key sections)
   - Abstract
   - Drawings information
   - Technical field/domain

### Phase 2: Claims Analysis

Use `review_patent_claims()` for automated analysis, then manually verify:

**Structural Requirements:**
- Independent claim completeness (all essential elements)
- Dependent claim proper reference format
- Claim numbering sequence (1, 2, 3...)
- Transitional phrases ("comprising", "consisting of", etc.)

**Definiteness (35 USC 112(b)):**
- Clear and unambiguous language
- No vague terms without context ("substantial", "about", etc.)
- Relative terms have reference points
- All limitations are definite

**Antecedent Basis:**
- First mention: "a" or "an"
- Later references: "the" or "said"
- All "the" references have prior "a/an" introduction
- Consistent terminology throughout

**MPEP References for Claims:**
```python
search_mpep(query="claim definiteness 112(b)", top_k=5)
get_mpep_section(section_number="2173")  # Claims support
get_mpep_section(section_number="2111")  # Claim interpretation
```

### Phase 3: Specification Review

Use `review_specification()` for automated checks, then analyze:

**Written Description (35 USC 112(a)):**
- Demonstrates possession of claimed invention
- All claim limitations are described
- Sufficient detail for PHOSITA understanding
- Examples and embodiments provided

**Enablement (35 USC 112(a)):**
- Person skilled in art can make and use invention
- Working examples provided (if needed)
- No undue experimentation required
- Scope matches claim breadth

**Best Mode (35 USC 112(a)):**
- Preferred embodiment disclosed
- Critical details included
- Note: AIA - no longer invalidity grounds but still required

**Claim Support Matrix:**
Create table mapping each claim element to specification location:

| Claim Element | Described? | Spec Location | Adequacy |
|--------------|-----------|---------------|----------|
| Element 1    | ✓         | Para [0025]   | Adequate |
| Element 2    | ⚠         | Para [0030]   | More detail needed |

**MPEP References for Specification:**
```python
search_mpep(query="written description requirement 112(a)", top_k=5)
search_mpep(query="enablement scope of claims", top_k=5)
get_mpep_section(section_number="2163")  # Written description
get_mpep_section(section_number="2164")  # Enablement
```

### Phase 4: Formalities Check

Use `check_formalities()` for each requirement:

**Abstract (MPEP 608.01(b)):**
- Length: 150 words or less
- Content: Technical disclosure only
- No commercial language
- Single paragraph format

**Title (MPEP 606):**
- Length: 500 characters or less
- Descriptive of invention
- No trademarks or proper names
- Technical and specific

**Drawings (MPEP 608.02):**
- All claim features illustrated
- Proper numbering (consecutive)
- Reference numerals consistent with spec
- Lead lines clear
- Sheet numbering correct

**Required Sections:**
- [ ] Field of Invention
- [ ] Background
- [ ] Summary
- [ ] Detailed Description
- [ ] Claims
- [ ] Abstract
- [ ] Cross-references (if applicable)

**MPEP References for Formalities:**
```python
get_mpep_section(section_number="608")    # Completeness
check_formalities(check_type="abstract")
check_formalities(check_type="drawings")
```

### Phase 5: Prior Art Research

Use prior art tools to identify similar inventions:

**Local Corpus Search (9.2M+ patents):**
```python
# Semantic search for similar inventions
search_prior_art(
    query="[description of invention]",
    top_k=10,
    cpc_filter="G06F",  # Optional: filter by technology class
    date_range=("20200101", "20251231")  # Optional: recent patents
)

# Get full details of relevant patents
get_patent_details(patent_id="10123456")
```

**USPTO API Search (Live Data):**
```python
# Search recently granted patents
search_uspto_api(
    query="neural network training",
    grant_from_date="2025-01-01",
    grant_to_date="2025-12-31"
)

# Get specific patent
get_uspto_patent(patent_number="US11234567")

# Check recent grants
get_recent_uspto_patents(days_back=30)
```

**Prior Art Analysis:**
- Identify closest prior art
- Note key differences from claimed invention
- Assess patentability implications
- Flag potential 102/103 issues

### Phase 6: Technical Diagrams

If drawings needed, use diagram tools:

**Generate Flowcharts:**
```python
create_flowchart(
    title="Authentication Process",
    steps=["Start", "Receive credentials", "Validate", "Grant access", "End"]
)
```

**Generate Block Diagrams:**
```python
create_block_diagram(
    title="System Architecture",
    components=[
        {"id": "sensor", "label": "Sensor"},
        {"id": "processor", "label": "Processor"},
        {"id": "display", "label": "Display"}
    ]
)
```

**Add Reference Numbers:**
```python
add_diagram_references(
    svg_path="diagram.svg",
    references={"sensor": "10", "processor": "20", "display": "30"}
)
```

## Report Generation

### Comprehensive Review Report Format

```markdown
# Patent Application Review Report

**Date:** [Current Date]
**Application Type:** Utility Patent (Non-Provisional)

---

## Executive Summary

### Overall Readiness: [Ready to File / Minor Revisions Needed / Major Revisions Required]

[2-3 paragraph assessment of application quality and readiness]

**Issue Summary:**
- Critical Issues: [X] (must fix before filing)
- Important Issues: [Y] (strongly recommend fixing)
- Minor Improvements: [Z] (consider addressing)

---

## Claims Analysis

### Status: ✓ COMPLIANT / ⚠ CONCERNS / ✗ NON-COMPLIANT

[Summary of claims analysis from review_patent_claims]

**Key Findings:**
1. [Finding 1 with MPEP citation]
2. [Finding 2 with MPEP citation]

**Claim-by-Claim Review:**

#### Claim 1 (Independent)
[Full claim text]

**Analysis:**
- Format: ✓ Proper
- Definiteness: ⚠ Term "substantially" lacks context (MPEP 2173.05(b))
- Antecedent Basis: ✓ All terms properly introduced
- Completeness: ✓ All essential elements present

---

## Specification Analysis

### Status: ✓ ADEQUATE / ⚠ CONCERNS / ✗ INSUFFICIENT

**Written Description:**
- Status: [Assessment]
- MPEP Citations: MPEP 2163, MPEP 2173
- Findings: [Details]

**Enablement:**
- Status: [Assessment]
- MPEP Citations: MPEP 2164
- Working Examples: [Present/Absent, Adequate/Inadequate]
- Findings: [Details]

**Best Mode:**
- Status: [Assessment]
- Note: Not grounds for invalidity under AIA
- Findings: [Details]

**Claim Support Matrix:**
| Claim Element | Spec Location | Adequacy | Issues |
|--------------|---------------|----------|--------|
| [Element]    | Para [X]      | ✓/⚠/✗    | [Note] |

---

## Formalities Check

**Abstract:**
- Word Count: [X] words
- Status: ✓ COMPLIANT / ✗ NON-COMPLIANT
- Issues: [If any]
- MPEP: 608.01(b)

**Title:**
- Character Count: [X] characters
- Status: ✓ COMPLIANT / ✗ NON-COMPLIANT
- Current Title: "[Title]"
- Issues: [If any]
- MPEP: 606

**Drawings:**
- Status: ✓ COMPLIANT / ⚠ REVIEW / ✗ NON-COMPLIANT
- All claim features shown: ✓/✗
- Proper numbering: ✓/✗
- Reference numerals consistent: ✓/✗
- MPEP: 608.02

**Required Sections:**
| Section | Present | Adequate | Notes |
|---------|---------|----------|-------|
| Field of Invention | ✓/✗ | ✓/✗ | [...] |
| Background | ✓/✗ | ✓/✗ | [...] |
| Summary | ✓/✗ | ✓/✗ | [...] |
| Detailed Description | ✓/✗ | ✓/✗ | [...] |
| Claims | ✓/✗ | ✓/✗ | [...] |
| Abstract | ✓/✗ | ✓/✗ | [...] |

---

## Prior Art Analysis

**Search Strategy:**
- Local corpus search: [Yes/No]
- USPTO API search: [Yes/No]
- Date range: [YYYY-MM-DD to YYYY-MM-DD]
- Technology class: [CPC codes]

**Closest Prior Art:**
1. US[Patent Number] - [Title]
   - Similarity: [High/Medium/Low]
   - Key Differences: [List]
   - 102/103 Risk: [Assessment]

2. [Additional patents]

**Patentability Assessment:**
[Overall assessment of patentability in view of prior art]

---

## CRITICAL ISSUES - MUST FIX BEFORE FILING

### 1. [Issue Title]
- **Location:** Claims/Specification/Formalities
- **Description:** [Specific issue]
- **MPEP Citation:** MPEP [Section]
- **Recommended Fix:** [Detailed solution]

### 2. [Additional critical issues]

---

## IMPORTANT ISSUES - STRONGLY RECOMMEND FIXING

### 1. [Issue Title]
- **Type:** Claims/Specification/Formalities
- **Description:** [Details]
- **MPEP Citation:** MPEP [Section]
- **Impact:** [Why this matters]
- **Recommended Fix:** [Solution]

---

## MINOR IMPROVEMENTS - CONSIDER ADDRESSING

### 1. [Improvement Title]
- **Type:** Claims/Specification/Formalities
- **Description:** [Details]
- **Benefit:** [Why fix this]
- **Suggestion:** [How to improve]

---

## MPEP REFERENCES CITED

| MPEP Section | Topic | Application |
|--------------|-------|-------------|
| MPEP 608 | Completeness | [How cited] |
| MPEP 2163 | Written Description | [How cited] |
| MPEP 2173 | Claims Support | [How cited] |
| [Additional] | [Topic] | [Application] |

---

## ACTION ITEMS CHECKLIST

### Must Do Before Filing:
- [ ] [Action item 1 - Critical]
- [ ] [Action item 2 - Critical]

### Should Do Before Filing:
- [ ] [Action item 1 - Important]
- [ ] [Action item 2 - Important]

### Consider Doing:
- [ ] [Action item 1 - Minor]
- [ ] [Action item 2 - Minor]

---

## FILING READINESS ASSESSMENT

**Current Status:** [Ready / Needs Minor Revisions / Needs Major Revisions]

**Estimated Time to Filing Readiness:**
- If no critical issues: Ready now
- If minor critical issues: 1-3 days
- If major critical issues: 1-2 weeks
- If fundamental issues: Substantial revision needed

**Next Steps:**
1. [Immediate action]
2. [Follow-up action]
3. [Final verification]

---

## USPTO FILING RESOURCES

**Filing Methods:**
- EFS-Web: https://www.uspto.gov/patents/apply/filing-online
- Patent Center: https://patentcenter.uspto.gov

**Fee Information:**
- Fee Schedule: https://www.uspto.gov/learning-and-resources/fees-and-payment
- Entity Status: [Micro / Small / Large]
- Estimated Fees: $[Amount] (based on claim count and entity size)

**Required Forms:**
- Form PTO/AIA/01: Declaration
- Form SB/08: IDS (if prior art known)
- Form 1449: IDS Citation List

**Contact:**
- USPTO Customer Service: 1-800-786-9199
- USPTO Email: usptoinfo@uspto.gov

---

## FOLLOW-UP SUPPORT

I'm available to:
- Review revised sections after addressing issues
- Generate technical drawings for your application
- Search for additional prior art
- Clarify any findings or recommendations
- Assist with IDS preparation

**What would you like to address first?**
```

## Key MPEP Sections Reference

### Claims & Claim Support
- **MPEP 608.01(i)** - Format of Claims
- **MPEP 2111** - Claim Interpretation
- **MPEP 2173** - Claims Must Be Supported
- **MPEP 2173.05(e)** - Antecedent Basis
- **MPEP 2173.05(g)** - Relative Terminology

### Specification Requirements
- **MPEP 2161** - Three Requirements of 35 USC 112(a)
- **MPEP 2163** - Written Description Guidelines
- **MPEP 2164** - Enablement Guidelines
- **MPEP 2165** - Best Mode Requirement

### Formalities
- **MPEP 606** - Title of Invention
- **MPEP 608** - Completeness of Application
- **MPEP 608.01(b)** - Abstract
- **MPEP 608.02** - Drawings

### Patentability
- **MPEP 2100** - Patentability Overview
- **MPEP 2131** - Anticipation (102)
- **MPEP 2141** - Obviousness (103)

## Best Practices

1. **Always Cite MPEP** - Every finding must reference specific MPEP sections
2. **Be Specific** - Provide exact locations (paragraph numbers, claim numbers)
3. **Explain Clearly** - State the issue, why it's problematic, and MPEP basis
4. **Suggest Fixes** - Don't just identify problems, provide solutions
5. **Prioritize** - Critical (must fix) > Important (should fix) > Minor (consider)
6. **Be Thorough** - Check all requirements systematically
7. **Stay Current** - Use latest MPEP edition and recent updates

## Common Critical Issues

### Must Flag Immediately:
- Missing antecedent basis ("the" without prior "a/an")
- Claim limitations not described in specification
- Abstract exceeds 150 words
- Missing required sections (Background, Summary, etc.)
- Drawings don't show all claimed features
- Indefinite claim terms without context

### Important to Address:
- Inconsistent terminology between claims and spec
- Insufficient working examples
- Vague transitional phrases
- Poor claim dependency structure
- Scope issues (claims broader than enablement)

### Minor Improvements:
- Non-optimal claim language
- Additional embodiments could strengthen
- Drawing quality could be enhanced
- Additional background context helpful

## Slash Command Integration

This skill works seamlessly with project slash commands:
- `/create-patent` - **NEW** Complete patent creation workflow with automatic validation
- `/review-claims` - Focused claims analysis
- `/review-specification` - Specification-only review
- `/review-formalities` - Formalities check only
- `/full-review` - Comprehensive multi-agent review

**Workflow Recommendation:**
- Use `/create-patent` when drafting NEW applications (includes automatic validation)
- Use `/full-review` when reviewing EXISTING complete applications
- Use specific review commands when checking individual sections

When user invokes these commands, provide the corresponding focused analysis using the appropriate MCP tools.

## Example Interaction

**User:** "Review my patent application claims for compliance"

**Response:**
1. Request claims text from user
2. Run `review_patent_claims(claims_text="[user's claims]")`
3. Search relevant MPEP: `search_mpep(query="claim definiteness 112", top_k=5)`
4. Perform manual analysis (antecedent basis, definiteness, structure)
5. Generate detailed report with findings, MPEP citations, and recommendations
6. Offer to review other sections or address specific concerns

---

**DISCLAIMER:** This tool assists with patent application preparation but does NOT replace legal advice from a registered patent attorney. Always consult with legal counsel before filing. Not affiliated with or endorsed by the USPTO.
