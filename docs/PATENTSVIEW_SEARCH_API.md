# Utility Patent Reviewer

A comprehensive Claude Code skill for advanced patent searching and prior art analysis using the PatentsView Search API.

## Overview

This project provides a powerful skill for Claude Code that enables sophisticated patent research, prior art searches, competitive intelligence, and technology landscape analysis. It integrates with the PatentsView Search API to access millions of US patents with rich metadata.

## Features

### 🔍 **Advanced Patent Search**
- Search by title, abstract, keywords, or full text
- Filter by inventor, assignee, classification, or date range
- Complex Boolean queries with AND/OR/NOT operators
- Citation network analysis

### 📊 **Prior Art Research**
- Find relevant patents before specific dates
- Comprehensive novelty assessments
- Multiple search strategies (keywords, classifications, citations)
- Automated result ranking and filtering

### 🏢 **Competitive Intelligence**
- Analyze patent portfolios by company
- Track technology trends over time
- Identify key inventors and innovations
- Monitor competitor filing activity

### 🌐 **Technology Landscape Analysis**
- Aggregate patents by technology area
- Identify emerging trends and white space
- Map competitive landscape
- Generate patent statistics and reports

## Installation

This is a Claude Code skill that should be placed in your project's `.claude/skills/` directory or your personal skills directory.

### Project Installation

The skill is already included in this repository:
```
.claude/
  └── skills/
      └── patent-search/
          ├── SKILL.md          # Skill definition and instructions
          ├── README.md         # Detailed documentation
          ├── patent_search.py  # Python helper library
          ├── examples.md       # Usage examples
          └── requirements.txt  # Python dependencies (none required)
```

### Personal Installation

To use this skill across all your projects:

```bash
# Copy to personal skills directory
cp -r .claude/skills/patent-search ~/.claude/skills/

# Or create a symlink
ln -s $(pwd)/.claude/skills/patent-search ~/.claude/skills/patent-search
```

## Setup

### 1. Obtain API Key

Get your free API key from the PatentsView Help Center:

**👉 [Request API Key](https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18)**

**Important**:
- One key per person
- Do not request multiple keys
- Rate limit: 45 requests per minute

### 2. Set Environment Variable

```bash
export PATENTSVIEW_API_KEY="your_api_key_here"
```

For persistent setup:

```bash
# Bash
echo 'export PATENTSVIEW_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# Zsh
echo 'export PATENTSVIEW_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# Fish
echo 'set -gx PATENTSVIEW_API_KEY "your_api_key_here"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

## Usage

### From Claude Code

The skill is automatically available in Claude Code. Simply ask Claude to help with patent searches:

**Example prompts:**

```
"Search for patents about neural networks published before 2020"

"Find patents by Google related to machine learning"

"Look for prior art on wireless charging technologies before 2023"

"Analyze the patent landscape for autonomous vehicles"

"Find patents by inventor John Smith in biotechnology"

"Show me IBM's recent patents in quantum computing"
```

Claude will automatically invoke the patent-search skill and provide formatted results.

### Using the Helper Script

The included Python script can be used independently:

```python
from patent_search import PatentsViewAPI

# Initialize (uses PATENTSVIEW_API_KEY environment variable)
api = PatentsViewAPI()

# Search by title
results = api.search_by_title("quantum computing", limit=10)

# Prior art search
results = api.search_prior_art(
    keywords="blockchain distributed ledger",
    before_date="2020-01-01",
    limit=50
)

# Search by assignee
results = api.search_by_assignee("Apple", start_date="2023-01-01")

# Custom query
query = {
    "_and": [
        {"_text_any": {"patent_title": "artificial intelligence"}},
        {"_gte": {"patent_date": "2020-01-01"}},
        {"assignees.assignee_organization": {"_contains": "Google"}}
    ]
}
results = api.search(query)
```

## Documentation

- **[SKILL.md](.claude/skills/patent-search/SKILL.md)**: Complete API reference and skill documentation
- **[README.md](.claude/skills/patent-search/README.md)**: Detailed feature documentation
- **[examples.md](.claude/skills/patent-search/examples.md)**: Practical usage examples

## Capabilities

### Search Types

| Search Type | Description | Example |
|------------|-------------|---------|
| **Keyword** | Search title/abstract | "machine learning" |
| **Inventor** | Find by inventor name | "Smith, John" |
| **Assignee** | Search by company | "IBM" |
| **Date Range** | Filter by date | 2020-01-01 to 2023-12-31 |
| **Classification** | Search by CPC/USPC | CPC: G06F (Computing) |
| **Citation** | Forward/backward citations | Patents citing US10123456 |
| **Complex** | Boolean combinations | Title AND Date AND Assignee |

### Query Operators

- **Comparison**: `_eq`, `_neq`, `_gt`, `_gte`, `_lt`, `_lte`
- **String**: `_begins`, `_contains`
- **Text**: `_text_all`, `_text_any`, `_text_phrase`
- **Logical**: `_and`, `_or`, `_not`

### Available Fields

**Patent Info**: `patent_id`, `patent_title`, `patent_abstract`, `patent_date`, `patent_type`, `patent_num_claims`

**People & Orgs**: `inventors.inventor_name_*`, `assignees.assignee_organization`

**Classifications**: `cpc_current.*`, `uspc.*`

**Citations**: `cited_patents.*`, `citedby_patents.*`

**Location**: `inventors.inventor_city`, `inventors.inventor_state`, `inventors.inventor_country`

## Examples

### Prior Art Search

Find relevant patents for a wireless charging invention before a priority date:

```python
api = PatentsViewAPI()
results = api.search_prior_art(
    keywords="wireless charging power transfer inductive",
    before_date="2023-01-01",
    limit=100,
    search_abstract=True
)

for patent in results['patents']:
    print(f"{patent['patent_id']}: {patent['patent_title']}")
    print(f"  Date: {patent['patent_date']}")
    print(f"  https://patents.google.com/patent/US{patent['patent_id']}\n")
```

### Competitive Analysis

Analyze Apple's AR patents:

```python
results = api.search_by_assignee("Apple", start_date="2022-01-01", limit=100)

# Group by technology classification
classifications = {}
for patent in results['patents']:
    for cpc in patent.get('cpc_current', []):
        cpc_id = cpc.get('cpc_subsection_id', 'Unknown')
        classifications[cpc_id] = classifications.get(cpc_id, 0) + 1

print("Apple AR Technology Areas:")
for cpc, count in sorted(classifications.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{cpc}: {count} patents")
```

### Technology Landscape

Map the quantum computing patent landscape:

```bash
# Ask Claude:
"Analyze the quantum computing patent landscape from 2020-2024.
Who are the top assignees? What are the main technology areas?
Show trends over time."
```

## API Reference

### PatentsViewAPI Class

```python
api = PatentsViewAPI(api_key=None)  # Uses PATENTSVIEW_API_KEY env var if not provided

# Main search method
api.search(query, fields=None, sort=None, options=None, method="POST")

# Convenience methods
api.search_by_title(keywords, limit=100, start_date=None, end_date=None)
api.search_by_inventor(last_name, first_name=None, limit=100)
api.search_by_assignee(assignee, limit=100, start_date=None)
api.search_prior_art(keywords, before_date, limit=100, search_abstract=True)
api.get_all_pages(query, fields=None, sort=None, max_results=1000)
```

### Helper Functions

```python
format_patent(patent)  # Format a patent record for display
```

## Rate Limits & Best Practices

- **Rate Limit**: 45 requests per minute (automatically enforced by the helper script)
- **Pagination**: Use cursor-based pagination for large result sets
- **API Key**: One key per person; do not share or request multiple keys
- **Data Usage**: Results are for research; consult patent attorney for legal opinions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `403 Forbidden` | Check API key is set correctly |
| `429 Rate Limit` | Wait 60 seconds; script auto-handles this |
| `400 Bad Request` | Verify query JSON syntax and field names |
| No results | Try broader keywords, check date ranges |
| Slow responses | Reduce `limit` parameter, check API status |

## Resources

- **PatentsView API Docs**: https://search.patentsview.org/docs/
- **Interactive API Testing**: https://search.patentsview.org/swagger-ui/
- **API Status**: https://patentsview.statuspage.io/
- **Google Patents**: https://patents.google.com/
- **CPC Classification**: https://www.cooperativepatentclassification.org/
- **USPTO**: https://www.uspto.gov/

## Limitations

- **US Patents Only**: Only covers US patent grants
- **Data Lag**: May lag recent publications by a few weeks
- **Rate Limits**: 45 requests/minute may limit large bulk operations
- **Research Use**: Results are for research only; not legal advice

For international patent searches, use:
- **EPO Espacenet**: https://worldwide.espacenet.com/
- **WIPO PATENTSCOPE**: https://patentscope.wipo.int/
- **Google Patents**: https://patents.google.com/ (worldwide)

## Contributing

This is a Claude Code skill. To improve it:

1. Edit `.claude/skills/patent-search/SKILL.md` for skill instructions
2. Update `patent_search.py` for helper library enhancements
3. Add examples to `examples.md`
4. Test with various search scenarios

## License

This skill uses the PatentsView API, which provides data under the Creative Commons Attribution 4.0 International License.

## Support

- **PatentsView API Issues**: https://patentsview-support.atlassian.net/servicedesk/
- **Claude Code Issues**: https://github.com/anthropics/claude-code/issues

## Acknowledgments

Built using the [PatentsView](https://patentsview.org/) API, which aggregates patent data from the USPTO and other sources to support research and innovation.

---

**Made for Claude Code** • Advanced Patent Research • Prior Art Search • Competitive Intelligence
