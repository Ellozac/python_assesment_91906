import tkinter as tk
import queue
import json
import os
from typing import Dict, List, Union

class Order:
    def __init__(self, order_num, items, total_price):
        self.order_num = order_num
        self.items = items
        self.total_price = total_price
    
    @classmethod
    def from_json(self, json):
        return Order(json["order_number"], [x for x in json["items"]], json["total_price"])

class OrderManager:
    def __init__(self, file_path: str = "orders.json"):
        self.file_path = file_path
        self.queue = queue.Queue()
        self.load_orders()

    def load_orders(self) -> bool:
        if not os.path.exists(self.file_path):
            self.reset_json_file()
            return False

        with open(self.file_path, 'r') as file:
            try:
                data = json.load(file)
                if data and "orders" in data[0]:
                    for order in data[0]["orders"]:
                        self.queue.put(Order.from_json(order))
                    self.reset_json_file()
                    return True

            except json.JSONDecodeError:
                print("Invalid JSON. Resetting file.")
                self.reset_json_file()
        return False

    def reset_json_file(self) -> None:
        with open(self.file_path, 'w') as file:
            json.dump([], file)

    def remaining_orders(self) -> int:
        return self.queue.qsize()

    def get_next(self) -> Dict[str, Union[str, List[Dict[str, Union[str, int, float]]], float]] | None:
        if not self.queue.empty():
            return self.queue.get()
        return None

    def skip_order(self, order):
        self.queue.put(order)

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Order to Prepare") 
        self.orders = OrderManager()
        self.main()
    
    def main(self):
        if self.orders.remaining_orders():
            order = self.orders.get_next()
            self.clear_window()
            tk.Label(self.root, text=f"Preparing order {order.order_num}").pack()
            
            for i in order.items:
                tk.Label(self.root, text=f"{i['name']} x {i['quantity']}").pack()

            tk.Label(self.root, text=f"Total price: ${order.total_price}").pack()
            tk.Button(self.root, text="Complete", command=self.main).pack(pady=5)
            tk.Button(self.root, text='Skip', command=lambda: self.skip_order(order)).pack(pady=5)
        else:
            self.clear_window()
            x = tk.Label(self.root, text="There are currently no orders.")
            x.pack()
            self.root.after(1000, self.check_for_orders)

    
    def skip_order(self, order: Dict[str, Union[str, List[Dict[str, Union[str, int, float]]], float]]):
        self.orders.skip_order(order)
        self.main()
    
    def check_for_orders(self):
        if self.orders.load_orders():
            self.main()

        else:
            self.root.after(1000, self.check_for_orders)

    def clear_window(self):
        for i in self.root.winfo_children():
            i.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

