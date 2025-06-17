from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, functions as F
from Models.models import Song, OLAPDatabase


class MapReduce(ABC):
    @abstractmethod
    def mapReduce(self, songs: list):
        pass


class TopRankingSongs(MapReduce):
    def mapReduce(self, db, songs: list):
        # Start Spark session
        spark = SparkSession.builder \
            .appName("TopRankingSongs") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .getOrCreate()

        # Convert ORM objects to dictionaries
        songs_dict = [song.__dict__.copy() for song in songs]


        for d in songs_dict:
            d.pop('_sa_instance_state', None)

        if not songs_dict:
            print("No songs found in the database.")
            spark.stop()
            return

        # Load data into Spark DataFrame
        df = spark.createDataFrame(songs_dict)

        df.show()

        # Select top 20 songs based on count (i.e. most played)
        top_songs_df = df.orderBy(F.desc("count")).limit(20)

        top_songs_df.show()
        
        # Clear previous OLAP entries
        db.session.query(OLAPDatabase).delete()
        db.session.commit()

        # Save new top 20 entries
        for row in top_songs_df.collect():
            db.session.add(OLAPDatabase(**row.asDict()))
        db.session.commit()

        # Stop the Spark session
        spark.stop()


# Optional: sanity test for Spark setup
if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("SanityTest") \
        .getOrCreate()

    df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "val"])
    df.show()
    spark.stop()
