# dbt Test Commands - Quick Reference

## Basic Commands

```bash
# Run all tests
dbt test

# Run tests for specific model
dbt test -s crypto_raw
dbt test -s crypto_stage
dbt test -s crypto_curated

# Run with verbose output (see SQL queries)
dbt test -v

# Run tests and see failed records
dbt test --store-failures
```

## Generic Test Commands

### not_empty_string Test
```bash
# Run all not_empty_string tests
dbt test -s tag:not_empty_string

# Run for specific model
dbt test -s crypto_raw.not_empty_string
```

### price_in_range Test
```bash
# Run all price_in_range tests
dbt test -s tag:price_in_range

# Run for specific model
dbt test -s crypto_stage.price_in_range
```

### recency_check Test
```bash
# Run all recency checks
dbt test -s tag:recency_check

# Run for specific model
dbt test -s crypto_curated.recency_check
```

### no_duplicate_ids Test
```bash
# Run duplicate ID checks
dbt test -s tag:no_duplicate_ids

# Run for specific model
dbt test -s crypto_raw.no_duplicate_ids
```

## Selection Patterns

```bash
# Run tests for model and all parents
dbt test -s +crypto_stage

# Run tests for model and all children  
dbt test -s crypto_stage+

# Run tests for model, parents, and children
dbt test -s +crypto_stage+

# Run tests for multiple models
dbt test -s crypto_raw,crypto_stage,crypto_curated

# Run tests excluding a model
dbt test --exclude crypto_curated

# Run all tests by tag
dbt test -s tag:not_null
dbt test -s tag:unique
```

## Advanced Options

```bash
# Run tests in parallel (4 threads)
dbt test --threads 4

# Run with specific profiles/environment
dbt test --target dev
dbt test --target prod

# Run and generate docs
dbt test && dbt docs generate && dbt docs serve

# Dry run (parse without execution)
dbt parse

# Check test syntax
dbt debug
```

## View Test Results

```bash
# After running tests with --store-failures
# Check results in:
# target/failures/
# target/compiled/

# View test documentation
dbt docs serve
# Then navigate to Tests tab
```

## Example Workflow

```bash
# 1. Update schema.yml with tests
# Already done in models/bronze/schema.yml, models/silver/schema.yml, models/gold/schema.yml

# 2. Run tests for bronze layer
dbt test -s crypto_raw -v

# 3. Run tests for silver layer
dbt test -s crypto_stage -v

# 4. Run tests for gold layer
dbt test -s crypto_curated -v

# 5. Run all tests
dbt test

# 6. Store failures for debugging
dbt test --store-failures

# 7. Generate documentation
dbt docs generate
dbt docs serve
```

## Test Success Output

```
Running with dbt=1.10.0
Found 5 models, 27 data tests, 1 source, 464 macros

✅ test not_null_crypto_raw_id ......................... [PASS]
✅ test unique_crypto_raw_id ........................... [PASS]
✅ test not_empty_string_crypto_raw_symbol ............ [PASS]
✅ test price_in_range_crypto_stage_price ............ [PASS]
✅ test recency_check_crypto_curated_date_and_time ... [PASS]

All tests passed! ✨
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No tests found | Check schema.yml has `data_tests:` defined |
| "Table not found" error | Run `dbt run` first to create models |
| Tests timeout | Increase timeout in profiles.yml or reduce data scope |
| Unexpected failures | Run with `-v` flag to see actual SQL queries |
| Adapter errors | Verify AWS credentials and S3/Athena access |

---

**Your Generic Tests Are Ready to Use!** ✅

- `not_empty_string` - Validates columns have no empty strings
- `price_in_range` - Validates prices are within bounds
- `recency_check` - Ensures data is not stale  
- `no_duplicate_ids` - Prevents duplicate records in time windows
