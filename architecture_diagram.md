# 📊 Data Quality & Monitoring Architecture

## Complete Pipeline Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                  KAFKA → S3 → DBT → ATHENA PIPELINE                │
└────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │  KAFKA PRODUCER LAYER                                    │
    │  (Sends cryptocurrency data to Kafka topic)              │
    └─────────────────────┬──────────────────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────────────┐
    │  KAFKA TOPIC: selected_crypto_data                       │
    │  - Stores: BTC, ETH, XRP prices & details                │
    │  ◄─── MONITORING: Kafka Consumer Lag tracked             │
    └─────────────────────┬──────────────────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────────────┐
    │  ENHANCED KAFKA CONSUMER (kafka/consumer.py)             │
    │  ├─ Batches messages (100 per batch)                     │
    │  ├─ Error handling & retry logic                         │
    │  ├─ Structured logging (timestamps, metrics)             │
    │  ├─ Metrics: throughput, upload time, errors             │
    │  └─ Publishes to CloudWatch                              │
    └─────────────────────┬──────────────────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────────────┐
    │  AWS S3 BUCKET: gaurav-hudi-data                          │
    │  ├─ Partitioned: crypto_data/year/month/day/             │
    │  ├─ Format: JSON files (1 per batch)                     │
    │  └─ ◄─── MONITORING: S3 object count, ingestion rate     │
    └─────────────────────┬──────────────────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────────────┐
    │  ATHENA EXTERNAL TABLE: crypto_raw_data                  │
    │  └─ Queries S3 data using SQL                            │
    └─────────────────────┬──────────────────────────────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
           ▼                             ▼
    ┌─────────────────────┐     ┌──────────────────────┐
    │  DBT TRANSFORMATIONS│     │  DATA QUALITY TESTS  │
    │  (Bronze/Silver/Gold)      │  (dbt test)          │
    └─────────────────────┘     └──────────────────────┘
           │
           │
    ┌──────┴───────────────────────────────────┐
    │                                           │
    ▼                                           ▼
┌─────────────────────┐           ┌──────────────────────┐
│ BRONZE LAYER        │           │ BRONZE TESTS         │
│ (crypto_raw)        │           │ ├─ not_null          │
│ ├─ Raw Kafka data   │◄──────────┤ ├─ unique            │
│ ├─ Minimal parsing  │           │ ├─ not_empty_string  │
│ └─ As-is format     │           │ ├─ price_in_range    │
└─────────────────────┘           │ └─ no_duplicate_ids  │
           │                       └──────────────────────┘
           ▼
┌─────────────────────┐           ┌──────────────────────┐
│ SILVER LAYER        │           │ SILVER TESTS         │
│ (crypto_stage)      │           │ ├─ not_null          │
│ ├─ Cleaned data     │◄──────────┤ ├─ unique            │
│ ├─ Validated        │           │ ├─ accepted_values   │
│ ├─ Transformations  │           │ ├─ not_empty_string  │
│ └─ Business rules   │           │ ├─ price_in_range    │
└─────────────────────┘           │ └─ recency_check     │
           │                       └──────────────────────┘
           ▼
┌─────────────────────┐           ┌──────────────────────┐
│ GOLD LAYER          │           │ GOLD TESTS           │
│ (crypto_curated)    │           │ ├─ not_null          │
│ ├─ Analytics ready  │◄──────────┤ ├─ unique            │
│ ├─ Business metrics │           │ ├─ not_empty_string  │
│ ├─ Aggregations     │           │ ├─ price_in_range    │
│ └─ KPI dashboard    │           │ ├─ recency_check     │
└─────────────────────┘           │ └─ freshness (2h)    │
           │                       └──────────────────────┘
           ▼
    ┌──────────────────────────────────────────────────────────┐
    │  ANALYTICS & BI TOOLS                                    │
    │  - Tableau/Power BI dashboards                           │
    │  - Analytics queries                                     │
    │  - Business intelligence                                 │
    └──────────────────────────────────────────────────────────┘
```

## Monitoring & Observability Layer

```
┌────────────────────────────────────────────────────────────────────┐
│                     MONITORING FRAMEWORK                            │
└────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                   DATA QUALITY TESTS (dbt)                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📋 GENERIC TESTS (Reusable across models):                         │
│  ├─ not_empty_string()      → Prevents empty string values          │
│  ├─ price_in_range()        → Validates price within bounds         │
│  ├─ recency_check()         → Detects data older than N days        │
│  └─ no_duplicate_ids()      → Prevents duplicate IDs in timewindow  │
│                                                                       │
│  📋 BUILT-IN TESTS:                                                  │
│  ├─ not_null                → No NULL values allowed                │
│  ├─ unique                  → No duplicate values                    │
│  ├─ accepted_values         → Only specific values allowed           │
│  └─ relationships           → Foreign key validation                 │
│                                                                       │
│  📋 FRESHNESS CHECKS:                                                │
│  ├─ Gold layer: Error after 2 hours without update                  │
│  ├─ Silver layer: Warn after 3 days                                 │
│  └─ Bronze layer: Warn after 7 days                                 │
│                                                                       │
│  TEST EXECUTION:                                                     │
│  └─ Run: dbt test -s crypto_raw,crypto_stage,crypto_curated         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│              PERFORMANCE MONITORING (CloudWatch)                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📊 CONSUMER METRICS (from enhanced Kafka consumer):                 │
│  ├─ Messages Consumed       (Count of processed messages)            │
│  ├─ Batches Uploaded        (Number of successful S3 uploads)        │
│  ├─ Upload Errors           (Failed upload attempts)                 │
│  ├─ Throughput              (messages/second)                        │
│  └─ Upload Duration         (seconds per batch)                      │
│                                                                       │
│  📊 PIPELINE METRICS (from data_quality_monitor.py):                │
│  ├─ Kafka Consumer Lag      (Messages pending in topic)              │
│  ├─ S3 Objects (last hour)  (Ingestion rate)                         │
│  ├─ Batch Size              (Records per upload)                     │
│  └─ Publish Frequency       (Every 5 minutes)                        │
│                                                                       │
│  📊 CLOUDWATCH DASHBOARD:                                            │
│  ├─ Real-time graphs        (Updated every 5 minutes)                │
│  ├─ Alert thresholds        (Configurable per metric)                │
│  ├─ Trend analysis          (Historical performance)                 │
│  └─ Create: monitoring/create_dashboard.sh                           │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                  LOGGING & ALERTING                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📝 STRUCTURED LOGGING:                                              │
│  ├─ Consumer logs           (kafka/consumer.py)                      │
│  │  └─ Format: timestamp, level, message, metrics                   │
│  ├─ Monitoring logs         (monitoring/data_quality_monitor.py)     │
│  │  └─ Format: Kafka lag, S3 count, errors                          │
│  └─ dbt logs                (target/logs/)                           │
│     └─ Format: Test results, SQL queries, timing                    │
│                                                                       │
│  🚨 ALERT CONDITIONS:                                                │
│  ├─ Kafka Lag > 1000 messages                                        │
│  ├─ dbt test failures (any)                                          │
│  ├─ Upload errors > 5                                                │
│  ├─ Data staleness > 2 hours (Gold layer)                            │
│  ├─ Throughput < baseline                                            │
│  └─ S3 upload duration > 30 seconds                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Project File Structure

```
project/
├── kafka/                                    ← Kafka Layer
│   ├── producer.py                          (Sends data to Kafka)
│   ├── consumer.py                          (Enhanced with metrics)
│   └── requirements.txt
│
├── aws_dbt/src/kafka_athena_dbt/            ← DBT Project
│   ├── dbt_project.yml                      (Project config)
│   ├── profiles.yml                         (Athena connection)
│   │
│   ├── models/
│   │   ├── bronze/                          (Raw data)
│   │   │   ├── crypto_raw.sql               (From Athena)
│   │   │   └── schema.yml                   (Tests + metadata)
│   │   │
│   │   ├── silver/                          (Cleaned/staged)
│   │   │   ├── crypto_stage.sql             (Transformations)
│   │   │   └── schema.yml                   (Tests + metadata)
│   │   │
│   │   ├── gold/                            (Analytics ready)
│   │   │   ├── crypto_curated.sql           (Business metrics)
│   │   │   └── schema.yml                   (Tests + metadata)
│   │   │
│   │   └── example/
│   │       ├── my_first_dbt_model.sql
│   │       ├── my_second_dbt_model.sql
│   │       └── schema.yml
│   │
│   ├── tests/
│   │   ├── generic/                         (Reusable tests)
│   │   │   ├── not_empty_string.sql
│   │   │   ├── price_in_range.sql
│   │   │   └── recency_check.sql
│   │   │
│   │   └── specific/                        (Model-specific tests)
│   │       └── no_duplicate_ids.sql
│   │
│   ├── macros/                              (Reusable functions)
│   │   ├── generate_alias_schema.sql
│   │   ├── data_quality_check.sql
│   │   └── surrogate_key.sql
│   │
│   ├── seeds/                               (Static CSV data)
│   ├── snapshots/                           (SCD Type 2)
│   ├── analyses/                            (Ad-hoc queries)
│   └── target/                              (Generated files)
│
├── monitoring/                              ← Monitoring Layer
│   ├── data_quality_monitor.py              (Kafka lag + S3 tracking)
│   ├── create_dashboard.sh                  (CloudWatch setup)
│   ├── requirements.txt                     (Dependencies)
│   └── README.md                            (Detailed guide)
│
├── docker-compose.yml                       ← Docker setup
├── Dockerfile
├── requirements.txt                         ← Python dependencies
│
└── Documentation/
    ├── Readme.md                            (Original project README)
    ├── HOW_TO_RUN_TESTS.md                  (Test execution guide)
    ├── DBT_TEST_COMMANDS.md                 (Command reference)
    ├── ARCHITECTURE_DIAGRAM.md              (This file)
    ├── IMPLEMENTATION_COMPLETE.md           (Feature summary)
    ├── QUICK_START_MONITORING.md            (Quick setup)
    └── DATA_QUALITY_SETUP.md                (Detailed setup)
```

## Data Flow with Layer Details

```
KAFKA TOPIC (selected_crypto_data)
    │ Format: JSON (id, symbol, name, price, last_updated)
    │ Batch size: 100 messages per upload
    │
    ▼
KAFKA CONSUMER + METRICS LOGGING
    │ ├─ Validates message format
    │ ├─ Batches messages (100 per batch)
    │ ├─ Tracks: consumed count, upload time, errors
    │ └─ Publishes to CloudWatch
    │
    ▼
S3 BUCKET (gaurav-hudi-data/crypto_data/)
    │ Structure: year/month/day/crypto_data_HH-MM-SS.json
    │ Contains: Raw JSON arrays from Kafka
    │
    ▼
ATHENA EXTERNAL TABLE (crypto_raw_data)
    │ Query: SELECT from S3 using SQL
    │ Location: s3://gaurav-hudi-data/crypto_data/
    │
    ▼
DBT BRONZE LAYER (crypto_raw)
    │ Action: Minimal transformation (just reformatted)
    │ Tests: 11 total (null, unique, empty string, price range, etc.)
    │
    ▼
DBT SILVER LAYER (crypto_stage)
    │ Action: Clean, validate, apply business rules
    │ Tests: 11 total (null, unique, range, recency, etc.)
    │
    ▼
DBT GOLD LAYER (crypto_curated)
    │ Action: Analytics-ready aggregations & metrics
    │ Tests: 11 total (freshness < 2h guarantee)
    │
    ▼
ANALYTICS & BI
    └─ Dashboards, reports, insights
```

## Key Features

✅ **End-to-End Monitoring**: Kafka lag, S3 ingestion, dbt tests  
✅ **27+ Data Quality Tests**: Built-in + custom generic tests  
✅ **Structured Logging**: All metrics timestamped and JSON-compatible  
✅ **CloudWatch Integration**: Real-time metrics & dashboards  
✅ **Error Handling**: Batching with retry logic, graceful degradation  
✅ **Scalable Architecture**: Handles high-volume Kafka streams  
✅ **Complete Documentation**: Setup guides, troubleshooting, examples  

---

**Last Updated**: February 6, 2026  
**Status**: ✅ Production Ready

│  └─ S3 Objects (last hour) (ingestion rate)                 │
│                                                               │
│  VISUALIZATION:                                              │
│  └─ CloudWatch Dashboard   (Real-time graphs + alarms)      │
│                                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    LOGGING & ALERTS                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Consumer Logs:                                              │
│  ├─ Timestamp: 2026-02-06 10:15:30                         │
│  ├─ Level: INFO/WARNING/ERROR                              │
│  ├─ Message: Progress update or error                      │
│  └─ Statistics on shutdown                                  │
│                                                               │
│  Monitoring Logs:                                            │
│  ├─ Kafka lag calculation                                   │
│  ├─ S3 object count                                         │
│  └─ CloudWatch publish status                               │
│                                                               │
│  Alert Thresholds (Configurable):                           │
│  ├─ Kafka Lag > 1000 messages                              │
│  ├─ Upload Errors > 5                                       │
│  ├─ Data staleness > 2 hours                                │
│  └─ Throughput < baseline                                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
                    ┌─────────────────────┐
                    │   Your Workspace    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────┐          ┌────────┐          ┌──────────┐
    │ Kafka  │          │   S3   │          │ Athena   │
    │        │          │ Bucket │          │          │
    └─┬──────┘          └────────┘          └──────────┘
      │                                           ▲
      │  Messages                                 │
      │                                      SQL Query
      ▼                                           │
    ┌────────────────────────────────────────────┼──────┐
    │  Enhanced Consumer (kafka/consumer.py)      │      │
    │  ├─ Batch messages (100)                   │      │
    │  ├─ Upload to S3                           │      │
    │  ├─ Track metrics                          │      │
    │  └─ Publish to CloudWatch ─────────┐       │      │
    └─────────────────────────────────────┼───────┘      │
                                         │              │
                                    ┌────▼──────┐       │
                                    │CloudWatch │       │
                                    │Metrics    │       │
                                    └───────────┘       │
                                                        │
                                         ┌──────────────┘
                                         │
                                         ▼
    ┌────────────────────────────────────────────────────┐
    │  dbt Models + Tests (aws_dbt/)                    │
    │  ├─ Bronze: crypto_raw (raw data)                │
    │  ├─ Silver: crypto_stage (staged & validated)    │
    │  └─ Gold: crypto_curated (ready for analytics)   │
    │                                                    │
    │  Tests Running:                                   │
    │  ├─ Null checks                                   │
    │  ├─ Uniqueness validation                         │
    │  ├─ Business rule validation                      │
    │  └─ Data freshness                                │
    └───────────────────────┬────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Gold Layer   │
                    │ Analytics    │
                    │ Ready Data   │
                    └──────────────┘
```

## File Organization

```
Project Root/
│
├── setup_monitoring.sh ..................... Automated setup script
├── IMPLEMENTATION_COMPLETE.md .............. This implementation summary
├── QUICK_START_MONITORING.md ............... Quick reference guide
├── DATA_QUALITY_SETUP.md ................... Setup details
│
├── monitoring/ ............................. Monitoring tools
│   ├── README.md ........................... Complete documentation
│   ├── data_quality_monitor.py ............. Kafka lag & S3 monitoring
│   ├── create_dashboard.sh ................. CloudWatch dashboard
│   └── requirements.txt .................... Dependencies
│
├── kafka/
│   └── consumer.py ......................... Enhanced with metrics
│
├── aws_dbt/src/kafka_athena_dbt/
│   ├── models/
│   │   ├── bronze/
│   │   │   ├── crypto_raw.sql
│   │   │   └── schema.yml .................. Bronze tests
│   │   ├── silver/
│   │   │   ├── crypto_stage.sql
│   │   │   └── schema.yml .................. Silver tests
│   │   └── gold/
│   │       ├── crypto_curated.sql
│   │       └── schema.yml .................. Gold tests
│   └── tests/
│       ├── generic/
│       │   ├── not_empty_string.sql
│       │   ├── price_in_range.sql
│       │   ├── recency_check.sql
│       │   └── no_duplicate_ids.sql
│       └── specific/
│           └── no_duplicate_ids.sql
│
└── docker-compose.yml
    Dockerfile
    requirements.txt
    ...
```

---

**Complete Data Quality & Monitoring System** ✅
