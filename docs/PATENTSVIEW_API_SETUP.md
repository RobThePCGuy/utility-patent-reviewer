# PatentsView Search API Setup

Complete guide for setting up the PatentsView Search API to enable advanced patent searching with filtering by inventor, assignee, classification, citations, and more.

## Overview

The PatentsView Search API provides access to millions of US patents with rich metadata. Perfect for competitive intelligence, prior art searches, and technology landscape analysis.

## Setup Steps

### 1. Request API Key

**Get your free API key:**
- Visit the [PatentsView Help Center](https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18)
- Submit a request for an API key
- Wait for email confirmation (usually within 24 hours)

**Important:**
- **One key per person** - Do not request multiple keys
- Keys are free for research and non-commercial use
- Rate limit: **45 requests per minute**

### 2. Set Environment Variable

Set the `PATENTSVIEW_API_KEY` environment variable with your key.

**See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for platform-specific instructions.**

Quick reference:

**Windows:**
```powershell
[System.Environment]::SetEnvironmentVariable('PATENTSVIEW_API_KEY', 'your_key_here', 'User')
```

**Linux/macOS:**
```bash
echo 'export PATENTSVIEW_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify Setup

The skill will automatically detect your API key. Test it by asking Claude Code:

```
"Search for patents about machine learning"
"Find patents by Google from the last year"
```

## Usage

Once configured, simply ask Claude Code natural language questions:

- "Find patents by [company] about [technology]"
- "Search for prior art on [invention] before [date]"
- "Analyze [company]'s patent portfolio in [technology area]"

## Capabilities

- **Search by**: Title, abstract, inventor, assignee (company), date range, classification
- **Advanced queries**: Boolean operators (AND/OR/NOT), phrase matching, wildcards
- **Citation analysis**: Forward and backward citations
- **Competitive intelligence**: Portfolio analysis, technology trends
- **Prior art research**: Comprehensive searches with date filtering

## Rate Limits

- **45 requests per minute** per API key
- The system automatically handles rate limiting
- For large batch operations, requests are automatically paced

## Resources

- **API Documentation**: https://search.patentsview.org/docs/
- **Interactive Testing**: https://search.patentsview.org/swagger-ui/
- **API Status**: https://patentsview.statuspage.io/
- **Complete Feature Guide**: [PATENTSVIEW_SEARCH_API.md](PATENTSVIEW_SEARCH_API.md)
- **Skill Documentation**: [docs/skills/patent-search/README.md](skills/patent-search/README.md)
- **Python Helper Script**: [docs/skills/patent-search/patent_search.py](skills/patent-search/patent_search.py)
- **Usage Examples**: [docs/skills/patent-search/examples.md](skills/patent-search/examples.md)

## Troubleshooting

| Error | Solution |
|-------|----------|
| `403 Forbidden` | Verify API key is set correctly: `echo $PATENTSVIEW_API_KEY` |
| `429 Rate Limit` | Wait 60 seconds. System auto-handles rate limiting. |
| `400 Bad Request` | Query syntax error. Check logs for details. |
| No results | Try broader keywords or different search terms. |

## Support

For PatentsView API issues:
- Help Center: https://patentsview-support.atlassian.net/servicedesk/

For skill/integration issues:
- GitHub Issues: https://github.com/RobThePCGuy/utility-patent-reviewer/issues
