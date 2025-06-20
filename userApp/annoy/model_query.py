import numpy as np
from typing import List
import logging

from annoy.model import Node

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

class QueryModel:
    def __init__(self, root : Node):
        self.root = root
    
    @staticmethod
    def _select_nearby(node :Node , q : np.ndarray, thresh : float):

        if not node._left and not node._right:
            return ()
        

        intercept = np.linalg.norm(q - node.hyperplane[0])

        if np.abs(intercept - node.hyperplane[1]) < thresh:
            return (node._left , node._right)
        if intercept < node.hyperplane[1]:
            return (node._left,)
        
        return (node.right,)


    @staticmethod
    def cosine_similarity(v1 : np.ndarray, v2 : np.ndarray):
        return np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))


    @staticmethod
    def _query_linear(nns : list, q_vec : np.ndarray, k : int) -> List[tuple]:
        logging.info("Linear query started!")
        
        try:
            linearq = sorted(nns , key=lambda v: QueryModel.cosine_similarity(v[1],q_vec))[-k:]
        except Exception as e:
            logging.error(f"Error during linear query: {e}")
            return []
        
        logging.info("Linear query compleated!")
        return linearq


    def query_tree(self, q_vec : np.ndarray , k :int) -> List[tuple]:

        logging.info("Query on tree started!")
        pq = [self.root]
        nns = []

        while pq:
            node = pq.pop(0)
            nearby = self._select_nearby(node , q_vec, 2.4)

            if nearby:
                pq.extend(nearby)
            else:
                nns.extend(node.songs)

        unranklist = self._query_linear(nns, q_vec, k)

        logging.info("Query tree compleated!")
        return unranklist