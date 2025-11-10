---
description: Create a complete non-provisional patent application with guided workflow and automatic validation
model: claude-sonnet-4-5-20250929
---

# Create Patent Application

Complete workflow to draft a USPTO-ready patent application from concept to validated filing package.

## What You'll Get

A complete patent application package including:
1. **Full Specification** - Background, Summary, Detailed Description
2. **Claims** - Independent and dependent claims (strategic coverage)
3. **Abstract** - USPTO-compliant (≤150 words)
4. **Drawings** - Patent-style technical diagrams (SVG/PNG)
5. **Validation Report** - Automatic USPTO compliance review
6. **Filing Summary** - Readiness assessment and next steps

## How It Works

This command uses a structured 6-phase workflow with automatic validation:

### Phase 1: Discovery & Requirements Gathering
I'll ask you about:
- Your invention (what problem does it solve?)
- Prior art awareness (what already exists?)
- Technical details (how does it work?)
- Key innovations (what's novel?)
- Document type (manuscript tool, hardware system, software method, etc.)
- Focus areas (specific aspects to emphasize)

### Phase 2: Technology Analysis
I'll analyze your invention to identify:
- Core technical innovations
- Key inventive aspects
- Differentiators from prior art
- Patentable subject matter
- Potential 101/102/103 issues

### Phase 3: Specification Drafting
I'll create a complete specification including:
- **Background** (problem statement, prior art analysis)
- **Summary** (objects of invention, technical solution)
- **Detailed Description** (implementation details, algorithms, embodiments)
- Numbered paragraphs (e.g., [0001], [0002]...)
- MPEP-compliant structure

### Phase 4: Claims Drafting
I'll draft strategic claims:
- **Independent Claims** (system, method, CRM)
- **Dependent Claims** (narrow features, fallback positions)
- Proper antecedent basis ("a/an" then "the")
- Clear, definite language
- Strategic claim ladder (broad → narrow)

### Phase 5: Diagrams & Abstract
I'll generate:
- **Technical Diagrams** using MCP diagram tools:
  - System architecture block diagrams
  - Process flowcharts
  - State machines
  - UML class diagrams
  - Timing diagrams
- **Abstract** (≤150 words, technical disclosure only)

### Phase 6: Automatic Validation
I'll automatically run `/full-review` on the created application to:
- Check claims for 35 USC 112(b) compliance
- Verify specification adequacy (35 USC 112(a))
- Validate formalities (MPEP 608)
- Identify any issues before you file
- Generate prioritized fix list

## Workflow Process

I'll use TodoWrite to track progress through these tasks:

```
✓ Gather requirements and invention details
✓ Analyze technology and identify innovations
✓ Draft specification (Background, Summary, Description)
✓ Draft claims (independent + dependent)
✓ Create technical diagrams
✓ Generate abstract
→ Run automatic validation (/full-review)
✓ Provide filing readiness assessment
```

## What I Need From You

### Required Information:
1. **Invention Description**
   - What does it do?
   - What problem does it solve?
   - How is it different from existing solutions?

2. **Technical Details**
   - Key algorithms or processes
   - System architecture or components
   - Data structures or schemas
   - Implementation approach

3. **Prior Art Context** (optional but helpful)
   - Existing tools/patents you know about
   - What makes your invention different
   - Any prior art searches conducted

### Optional Information:
- Existing documentation (design docs, code, diagrams)
- Specific claims you want covered
- Particular focus areas or innovations to emphasize
- Target patent scope (broad vs. narrow)
- Timeline constraints

## When to Use This Command

Use `/create-patent` when:
- ✓ You have a complete invention ready to patent
- ✓ You want guided patent drafting assistance
- ✓ You want automatic validation of the draft
- ✓ You need a USPTO-ready filing package

Don't use this command if:
- ✗ You already have a complete draft (use `/full-review` instead)
- ✗ You only need specific sections reviewed (use `/review-claims` or `/review-specification`)
- ✗ You're not ready to describe your invention in detail

## Output Files

I'll create these files:
- `PATENT_APPLICATION_[INVENTION_NAME].md` - Complete specification + claims
- `PATENT_SUMMARY_[INVENTION_NAME].md` - Filing package summary
- `FIG*.svg` - Technical diagrams (in diagrams/ directory)
- `USPTO_REVIEW_REPORT_[INVENTION_NAME].md` - Validation results

## Key Features

### 1. Automatic Prior Art Differentiation
I'll help articulate how your invention differs from prior art by:
- Analyzing known prior art systems
- Identifying specific technical combinations
- Emphasizing unexpected technical benefits
- Positioning for 102/103 compliance

### 2. Strategic Claim Coverage
I'll draft claims with:
- Broad independent claims (maximum protection)
- Narrow dependent claims (fallback positions)
- Alternative implementations (design-around prevention)
- Method + system + CRM claims (triple coverage)

### 3. Alice Framework Compliance
I'll ensure 35 USC 101 eligibility by:
- Reciting specific technical improvements
- Including concrete data structures
- Specifying measurable technical effects
- Avoiding abstract idea rejection

### 4. Measurable Technical Effects
I'll emphasize quantifiable improvements:
- Performance gains (e.g., "60-80% reduction")
- Technical problem solutions
- Computer functionality improvements
- Specific technical advantages over prior art

### 5. MCP Tool Integration
I'll use specialized tools for:
- `create_block_diagram()` - System architectures
- `create_flowchart()` - Process flows
- `render_diagram()` - Custom DOT diagrams
- `search_mpep()` - MPEP compliance checking
- `review_patent_claims()` - Automated claims analysis
- `/full-review` - Comprehensive validation

## Example Usage

**You:** `/create-patent`

**Me:**
```
I'll help you create a complete USPTO-ready patent application!

Let me start by understanding your invention.

**Question 1: What is your invention?**
Please describe what your invention does and what problem it solves.
(Provide 2-3 paragraphs explaining the technology)
```

[After you provide details, I'll proceed through all 6 phases]

**Me:**
```
✓ Phase 1-5 Complete: Patent application drafted
→ Phase 6: Running automatic validation...

Executing `/full-review` on your draft application...
[Validation results shown]

Your patent application is ready! Here's what I created:
- PATENT_APPLICATION_BIDIRECTIONAL_CONTINUITY.md (14,500 words)
- 7 technical diagrams (FIG1.svg - FIG7.svg)
- 30 claims (1 independent system, 1 method, 1 CRM, 27 dependent)
- USPTO compliance review completed

**Filing Readiness:** 95% ready (2 minor issues to address)
```

## Best Practices

### What Makes a Strong Patent:
1. **Specific Technical Solution** - Not just "use AI" but HOW you use it
2. **Concrete Data Structures** - Named schemas, graphs, indexes
3. **Measurable Effects** - Quantified improvements (%, time, cost)
4. **Clear Prior Art Distinction** - Explicit "Prior art does X, we do Y"
5. **Strategic Claim Ladder** - Broad → medium → narrow fallbacks

### What to Avoid:
1. ✗ Abstract ideas without technical implementation
2. ✗ Purely functional claiming without structure
3. ✗ Generic "computer does X" without technical improvement
4. ✗ Claims broader than specification support
5. ✗ Vague terms without definition ("substantial", "efficient")

## Validation Integration

After drafting, I automatically run:
```bash
/full-review [your-patent-application]
```

This parallel review checks:
- Claims compliance (35 USC 112(b))
- Specification adequacy (35 USC 112(a))
- Formalities (MPEP 608)
- Prior art concerns (if corpus available)

You'll receive:
- ✓ Ready to file (0 critical issues)
- ⚠ Minor revisions needed (1-3 issues)
- ✗ Major revisions required (4+ issues)

## Timeline Estimates

**Typical Duration:**
- Phase 1 (Discovery): 10-15 minutes
- Phase 2 (Analysis): 5 minutes
- Phase 3 (Specification): 15-20 minutes
- Phase 4 (Claims): 10-15 minutes
- Phase 5 (Diagrams): 10-15 minutes
- Phase 6 (Validation): 5-10 minutes
- **Total: 55-80 minutes** for complete USPTO-ready application

**Note:** Timeline varies based on invention complexity and your preparation level.

## Cost Considerations

**Using This Tool:**
- Free patent drafting assistance
- Automated USPTO compliance checking
- Professional-quality diagrams

**Additional Filing Costs:**
- USPTO fees: $425 (micro) / $850 (small) / $1,700 (large entity)
- Optional patent attorney review: $5,000-$15,000
- Optional professional patent drawings: $1,500-2,500

**Compared to Professional Drafting:**
- Patent attorney drafting: $10,000-$25,000
- Timeline: 4-8 weeks
- **Savings: ~$10,000-$25,000 and 4-8 weeks**

## Ready to Start?

When you invoke this command, I'll begin the discovery phase by asking about your invention. Have ready:
- Description of what your invention does
- Technical implementation details
- Known prior art or competing solutions
- Any existing documentation or diagrams

**Let's create your patent application!**

---

**DISCLAIMER:** This tool assists with patent application preparation but does NOT replace legal advice from a registered patent attorney. Always consult with legal counsel before filing. Not affiliated with or endorsed by the USPTO.
