from annoy.data_ingestion import ZipDataIngestor
from annoy.data_transformation import DataFrameToList, DataTranfromer
from annoy.model_traning import AnnoyModel
from annoy.model_query import QueryModel
from annoy.model import Node
import logging

logging.basicConfig(level=logging.INFO , format='%(asctime)s %(levelname)s %(meassage)s')

class pipline:
    def __init__(self):

        logging.info("Main Pipelining Has Started")

        file_path = "C:\\Projects\\root\\userApp\\Data Frame\\song_data.csv"
        sep = ";"
        data = ZipDataIngestor()
        df = data.ingest(file_path, sep)

        transformer = DataFrameToList()
        transformed_data = transformer.transform(df)

        # Training the model
        model = AnnoyModel(K=10, imb=0.5)
        root = Node(None , transformed_data)
        model.train(root)

        # Querying the model
        self.query = QueryModel(root)

        logging.info("Task Compleated! Closing pipeline.")


