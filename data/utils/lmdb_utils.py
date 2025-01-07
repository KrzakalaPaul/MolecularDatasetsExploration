import lmdb
import os
import pickle
from functools import lru_cache
import logging
import os 

logger = logging.getLogger(__name__)

def open_db(path, split, mapsize=1099511627776):
    file = os.path.join(path, f"{split}.lmdb")
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(file):
        os.remove(file)
    env = lmdb.open(
                    file,
                    subdir=False,
                    readonly=False,
                    lock=False,
                    readahead=False,
                    meminit=False,
                    max_readers=1,
                    map_size=mapsize
                    )
    return env
    
    
def format_db(env):
    with env.begin(write=True) as txn:
        cursor = txn.cursor()
        new_key = 0
        for key, value in cursor:
            txn.delete(key)
            txn.put(f"{new_key}".encode("ascii"), value)
            new_key += 1
        txn.put("size".encode("ascii"), str(new_key).encode("ascii"))
            
 
class LMDBDataset:
    def __init__(self, db_path, split="train"):
        self.db_path = db_path
        self.split = split
        assert os.path.isfile(self.db_path), "{} not found".format(self.db_path)
        env = self.connect_db(self.db_path)
        with env.begin() as txn:
            self._keys = list(txn.cursor().iternext(values=False))
        self.dataset_size = pickle.loads(env.begin().get(f"{self.split}_size".encode("ascii")))

    def connect_db(self, lmdb_path, save_to_self=False):
        env = lmdb.open(
            lmdb_path,
            subdir=False,
            readonly=True,
            lock=False,
            readahead=False,
            meminit=False,
            max_readers=256,
        )
        if not save_to_self:
            return env
        else:
            self.env = env

    def __len__(self):
        return self.dataset_size

    @lru_cache(maxsize=16)
    def __getitem__(self, idx):
        if not hasattr(self, "env"):
            self.connect_db(self.db_path, save_to_self=True)
        datapoint_pickled = self.env.begin().get(f"{self.split}_{idx}".encode("ascii"))
        data = pickle.loads(datapoint_pickled)
        return data
