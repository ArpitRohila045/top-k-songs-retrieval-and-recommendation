from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, functions as F
from Models.models import OLAPDatabase
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class MapReduce(ABC):
    @abstractmethod
    def execute(self, songs: list):
        pass


class TopRankingSongs(MapReduce):
    def execute(self, db, songs: list):

        # Start Spark session
        logging.info("MapReduce Job Started")
        try:
            spark = SparkSession.builder \
                .appName("TopRankingSongs") \
                .config("spark.driver.memory", "2g") \
                .config("spark.executor.memory", "2g") \
                .getOrCreate()
        except Exception as e:
            logging.error("Exception occurred! Spark session failed!")
            return
        
        logging.info("Spark Session initialized!")
        # Convert ORM objects to dictionaries
        songs_dict = [song.__dict__.copy() for song in songs]


        for d in songs_dict:
            d.pop('_sa_instance_state', None)

        if not songs_dict:
            print("No songs found in the database.")
            spark.stop()
            return

        # Load data into Spark DataFrame
        logging.info("Loading Spark Data Frame")
        df = spark.createDataFrame(songs_dict)
        logging.info("Load compleated")
        
        df.show()

        logging.info("Mapping started!")
        # Select top 20 songs based on count (i.e. most played)
        top_songs_df = df.orderBy(F.desc("count")).limit(20)
        logging.info("Mapping compleated!")
        logging.info("Reducing started!")

        top_songs_df.show()
        logging.info("Reducing compleated")

        # Clear previous OLAP entries
        logging.info("Updating (OLAP)Online Analytics Processing Database")
        db.session.query(OLAPDatabase).delete()
        db.session.commit()

        # Save new top 20 entries
        for row in top_songs_df.collect():
            db.session.add(OLAPDatabase(**row.asDict()))
        db.session.commit()

        logging.info("Update compleated")
        # Stop the Spark session
        spark.stop()
        logging.info("Spark session closed")

# Optional: sanity test for Spark setup
if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("SanityTest") \
        .getOrCreate()

    df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "val"])
    df.show()
    spark.stop()
