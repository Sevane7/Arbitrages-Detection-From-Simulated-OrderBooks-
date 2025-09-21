import numpy as np
import pandas as pd
from typing import List
from dataclasses import dataclass

class OrderBook:

    def __init__(self, name):

        self.name = name
        self.bids : pd.DataFrame = None
        self.asks : pd.DataFrame = None

    @classmethod
    def generate_orderbook(cls, 
                            name : str,
                            center_price : float,
                            spread : float,
                            nb_levels = 5,
                            min_qty = 1,
                            max_qty = 10, 
                            max_variance = 0.3):

        orderbk_obj = cls(name)

        best_bid = center_price - spread/2
        best_ask = center_price + spread/2

        bids = [[best_bid - i * np.abs(np.random.randn() * np.random.uniform(0, max_variance)), int(np.random.uniform(min_qty, max_qty))] for i in range(nb_levels)]
        asks = [[best_ask + i * np.abs(np.random.randn() * np.random.uniform(0, max_variance)), int(np.random.uniform(min_qty, max_qty))] for i in range(nb_levels)]
        
        orderbk_obj.bids = pd.DataFrame(bids, columns=["Price", "Quantity"]).round(2).groupby("Price").sum().sort_index(ascending=False).reset_index()
        orderbk_obj.asks = pd.DataFrame(asks, columns=["Price", "Quantity"]).round(2).groupby("Price").sum().sort_index(ascending=True).reset_index()

        # print(orderbk_obj.bids)
        return orderbk_obj

    @staticmethod
    def generate_multiple(symbol: str, n: int):
        books = []
        base_price = 340
        
        for i in range(n):
            center_price = base_price + np.random.uniform(-0.5, 0.5)  # petite variation
            spread = np.random.uniform(-0.3, 0.3)                     # spread +/- raisonnable
            max_var = np.random.uniform(0.1, 0.6)                     # variance plausible

            name = f"{symbol} exchange{i}"
            book = OrderBook.generate_orderbook(
                name,
                center_price=center_price,
                spread=spread,
                max_variance=max_var
            )
            print(book)
            books.append(book)
        
        return books


    def to_dict(self):
        return {
            "bids" : self.bids.to_numpy(),
            "asks" : self.asks.to_numpy()
        }

    def __str__(self):
        s = f"\n=========== {self.name} ===========\n"
        s += f"{'BIDS':>12} | {'ASKS':>12}\n"
        s += f"{'Price   Qty':>12} | {'Price   Qty':>12}\n"
        s += "-" * 28 + "\n"
        
        # Convertir en numpy arrays si ce ne l'est pas déjà
        bids = self.bids.to_numpy()
        asks = self.asks.to_numpy()
        
        # Prendre le maximum de niveaux entre bids et asks
        max_levels = max(len(bids) if len(bids) > 0 else 0, 
                        len(asks) if len(asks) > 0 else 0)
        
        for i in range(max_levels):
            # Formatage des bids
            if i < len(bids):
                bid_str = f"{bids[i][0]:>6.2f} {int(bids[i][1]):>3d}"
            else:
                bid_str = " " * 10  # Espaces vides si pas de bid
            
            # Formatage des asks
            if i < len(asks):
                ask_str = f"{asks[i][0]:>6.2f} {int(asks[i][1]):>3d}"
            else:
                ask_str = " " * 10  # Espaces vides si pas d'ask
            
            s += f"{bid_str:>12} | {ask_str:>12}\n"
        
        return s


@dataclass
class Results:
    exchange1 : str
    exchange2 : str
    bid : float
    ask : float
    opt_qty : int

class Arbitrages:

    def __init__(self, books : List[OrderBook]):
        
        for i, attr in enumerate(books):
            setattr(self, f"book_{i}", attr)
        
        self.num_books = len(books)
        self.all_books = books

        self.results : List[Results] = []

        self.run()

    
    @staticmethod
    def exists_arb(bids : np.ndarray, asks : np.ndarray) -> bool: 
        return bids[0][0] > asks[0][0]


    def check_in_results(self, ask_price : float, ask_qty : float, exchange : str) -> bool:
        """Check with the previous results if an ask quantity has been used or not.

        Args:
            ask_price (float): the ask price available or not.
            exchange (str): the exchange proposing the ask price.
            ask_qty (float): the quantity we actually wan to buy.

        Returns:
            bool: True we can proceed the arbitrage, False if all the ask price has been bought already.
        """
        
        if not self.results :
            return True
        
        else:
            df = pd.DataFrame([r.__dict__ for r in self.results])
            
            if exchange not in df["exchange2"].values:
                return True 
            
            else :
                df : pd.DataFrame= df[df["exchange2"] == exchange]
                if ask_price not in df["ask"].values:
                    return True
                else:
                    df = df[df["ask"] == ask_price]
                    return  df["opt_qty"].sum() < ask_qty

            
    def detect_arb(self, bids : np.ndarray, asks : np.ndarray, description : dict) -> None:

        while len(bids) > 0 and len(asks) > 0 and self.exists_arb(bids=bids, asks=asks):

            if not self.check_in_results(ask_price=asks[0][0], ask_qty=asks[0][1], exchange=description["exchange2"]):
                asks = np.delete(asks, 0, 0)
                continue

            # Save Arbitrage in self.results              
            res_tmp = Results(
                exchange1=description["exchange1"],
                exchange2=description["exchange2"],
                bid = bids[0][0],
                ask = asks[0][0],
                opt_qty = min(bids[0][1], asks[0][1])
            )
            self.results.append(res_tmp)

            # adapte and delete quantities
            if bids[0][1] > asks[0][1]:
                bids[0][1] -= asks[0][1]
                bids = np.delete(asks, 0, 0)
            
            elif bids[0][1] < asks[0][1]:
                asks[0][1] -= bids[0][1]
                asks = np.delete(bids, 0, 0)
            
            else : 
                bids = np.delete(bids, 0, 0)
                asks = np.delete(asks, 0, 0)
    
    def run(self):

        # for each i we compare bids_i with all the others asks
        for i, book_i in enumerate(self.all_books):
            bid_i, ask_i = book_i.bids.to_numpy(), book_i.asks.to_numpy()
            
            description = {
                "exchange1" : book_i.name.split(" ")[-1],
                "exchange2" : book_i.name.split(" ")[-1],
            }

            # 1) arbitrages within the book
            bid_i_tmp = bid_i
            self.detect_arb(bids = bid_i_tmp, asks= ask_i, description = description)
            
            # 2) arbitrages with other books
            idx_other_books = np.arange(self.num_books)
            idx_other_books = np.delete(idx_other_books, i)

            for j in idx_other_books:
                description["exchange2"] = self.all_books[j].name.split(" ")[-1]
                ask_j = self.all_books[j].asks.to_numpy()
                self.detect_arb(bids = bid_i, asks=ask_j, description=description)
        
        print(self)
    
    def __str__(self):
        df = pd.DataFrame([r.__dict__ for r in self.results])
        df["P&L"] = (df["bid"] - df["ask"]) * df["opt_qty"]
        res = "==" * 4 + "Results" + "==" * 4 + "\n"
        df.rename(columns={"exchange1" : "From",
                           "exchange2" : "To"}, inplace=True)
        res += df.to_string() + "\n"
        res += f"\n Total arbitrages detected (by asset quantity) = {int(df["opt_qty"].sum())}"
        res += f"\n Total P&L = {df["P&L"].sum().round(2)} {self.all_books[0].name.split("/")[0]}"

        return res



if __name__ == "__main__":
   
    books = OrderBook.generate_multiple(symbol = "SOL/USDT", n= 4)

    arb = Arbitrages(books=books)




    

        