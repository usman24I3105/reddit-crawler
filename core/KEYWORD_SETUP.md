# Keyword Setup Guide

This guide explains how to set up the keyword-based Reddit crawler system for fetching posts about people wanting to buy homes in California.

## Overview

The system uses:
1. **Keyword Templates**: Master templates with `{place}` placeholders
2. **Places List**: California cities, counties, and regions
3. **Intent Weights**: Scoring system for high-intent keywords
4. **Filters**: Exclude advertisements, keep only high-intent posts

## Quick Start

### Step 1: Generate Keywords

Generate keywords from templates and places:

```bash
cd core
python scripts/setup_keywords.py
```

This will:
- Generate keywords from `keywords/master_templates_v3_complete.txt` and `keywords/places_california_complete_v2.txt`
- Load them into the database as primary (intent) and secondary (places) keywords
- Filter out advertisement keywords

### Step 2: Verify Keywords

Check that keywords were loaded:

```bash
python scripts/init_keywords.py  # This will show keyword counts
```

Or check the database directly.

### Step 3: Run the Crawler

The crawler will now:
- Fetch posts from the last **12 hours** (not 24)
- Use **no limit** on number of posts
- Filter by keywords (primary + secondary match required)
- Exclude company advertisements
- Keep only high-intent posts (people wanting homes)

## Advanced Options

### Generate Only High-Scoring Keywords

Only generate keywords with intent score >= 10:

```bash
python scripts/setup_keywords.py --min-score 10
```

### Limit Number of Keywords

Generate only first 50,000 keywords:

```bash
python scripts/setup_keywords.py --limit 50000
```

### Load Existing Keywords File

If you already have a keywords file:

```bash
python scripts/setup_keywords.py --skip-generation --keywords-file keywords/generated_keywords.csv
```

## How It Works

### Keyword Classification

Keywords are classified as:
- **Primary (Intent)**: Phrases indicating someone wants to do something
  - Examples: "buy a house", "moving to", "first time home buyer"
- **Secondary (Places/Topics)**: California locations and topics
  - Examples: "Los Angeles", "San Francisco", "Orange County"

### Matching Rule

A post is kept ONLY IF:
- Contains at least 1 **primary** keyword (intent)
- Contains at least 1 **secondary** keyword (place/topic)

### Filtering

The system filters out:
1. **Advertisements**: Posts from companies/agents
   - Indicators: "real estate agent", "realtor", "contact us", URLs, etc.
2. **Low-Intent Posts**: Posts that don't indicate someone wants to buy
   - Only keeps posts with high-intent phrases

### Time Window

- Fetches posts from the last **12 hours** (configurable)
- No limit on number of posts (fetches all matching posts)

## Configuration

### Environment Variables

Update `.env` file:

```bash
# Crawler runs every 12 hours
CRAWLER_INTERVAL_HOURS=12

# Subreddits to search (comma-separated)
SUBREDDITS=Home,RealEstate,FirstTimeHomeBuyer,personalfinance

# No post limit (fetches all)
POST_LIMIT=1000  # Reddit API max, but we fetch all within time window
```

## Manual Keyword Generation

If you want to generate keywords manually:

```bash
cd keywords
python generate_keywords.py \
  --templates master_templates_v3_complete.txt \
  --places places_california_complete_v2.txt \
  --weights intent_weights_v2.json \
  --min-score 10 \
  --out generated_keywords.csv
```

Then load them:

```bash
cd core
python scripts/load_generated_keywords.py --keywords ../keywords/generated_keywords.csv
```

## Troubleshooting

### No Keywords Found

If the crawler finds no posts:
1. Check that keywords are loaded: `python scripts/init_keywords.py`
2. Verify keyword matching: Check logs for "KeywordFilter initialized"
3. Check subreddits: Make sure SUBREDDITS in .env includes relevant subreddits

### Too Many/Few Posts

Adjust filters:
- **More posts**: Lower `--min-score` when generating keywords
- **Fewer posts**: Increase `--min-score` or add more strict filters

### Advertisement Posts Getting Through

Update `core/src/filters/intent_filter.py`:
- Add more indicators to `AD_INDICATORS` list
- Strengthen `is_advertisement()` logic

## Files

- `keywords/generate_keywords.py`: Generates keywords from templates
- `keywords/master_templates_v3_complete.txt`: Intent templates
- `keywords/places_california_complete_v2.txt`: California places
- `keywords/intent_weights_v2.json`: Intent scoring weights
- `core/scripts/setup_keywords.py`: Master setup script
- `core/scripts/load_generated_keywords.py`: Loads keywords into DB
- `core/src/filters/intent_filter.py`: Filters ads and low-intent posts

