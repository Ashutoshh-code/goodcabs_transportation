from pyspark import pipelines as dp
import pyspark.sql.functions as F

SOURCE_PATH = "s3://goodcabs-ashutosh-9335/data_store/trips"

@dp.table(
    name = "transportation.bronze.trips",
    comment = "streaming ingestion of raw orders data with Auto loader",
    table_properties = {
        "quality": "bronze",
        "layer": "bronze",
        "source_format": "csv",
        "delta.enableChangeDataFeed": "true",
        "delta.autoOptimize.optimizeWrite": "true",
        "delta.autoOptimize.autoCompact": "true"
    }
)
def order_bronze():
    df = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .option("cloudFiles.maxFilesPerTrigger", 100)
        .load(SOURCE_PATH)
    )

    # Rename the problematic column
    df = df.withColumnRenamed(
        "distance_travelled(km)",
        "distance_travelled_km"
    )

    df = df.withColumn("file_name", F.col("_metadata.file_path")).withColumn("ingest_datetime", F.current_timestamp())

    return df