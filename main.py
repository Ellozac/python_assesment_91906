import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import queue
import json
import os
from typing import Dict, List, Union, Self
class Order:
    def __init__(self, order_num, items, total_price):
        self.order_num = order_num
        self.items = items
        self.total_price = total_price
    
    @classmethod
    def from_json(cls, json) -> Self:
        return cls(json["order_number"], [x for x in json["items"]], json["total_price"])

class OrderManager:
    def __init__(self, file_path: str = "./data/orders.json"):
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
                if data and len(data[0]["orders"]) > 0:
                    for order in data[0]["orders"]:
                        self.queue.put(Order.from_json(order))
                    self.reset_json_file()
                    return True
                else:
                    return False
            except ValueError:
                tk.messagebox.showerror(title="Error Invalid Json",message=f"Invalid JSON. {self.file_path}")
                if tk.messagebox.askyesno(title="Regenerate file?", message="Would you like to reset the file?"):
                    self.reset_json_file()
                else:
                    exit(1)
            except KeyError:
                self.reset_json_file()
        return False

    def reset_json_file(self) -> None:
        with open(self.file_path, 'w') as file:
            json.dump([{"orders": []}], file)

    def remaining_orders(self) -> int:
        return self.queue.qsize()

    def get_next(self) -> Order | None:
        if not self.queue.empty():
            return self.queue.get()
        return None

    def skip_order(self, order):
        self.queue.put(order)

class App:
    def __init__(self, root: tk.Tk, file_path="./data/orders.json"):
        self.root = root
        self.root.title("Order to Prepare")
        try: 
            self.orders = OrderManager(file_path)
        except FileNotFoundError:
            if tk.messagebox.askyesno(title=f"{file_path} Not Found", message="File not found. Create it?"):
                os.mkdir(Path(file_path).parent)
                with open(file_path, "w") as file:
                    file.write("[]")
                self.orders = OrderManager(file_path)
            else:
                exit(1)
        self.check_manager()
        self.main()
    def check_manager(self):
        ans = simpledialog.askstring("robot check", "whats 9 + 10")
        while not ans.isdigit():
            messagebox.showerror("Error", "Please only type numbers.")
            ans = simpledialog.askstring("robot check", "whats 9 + 10")
        if not int(ans) == 19:
            messagebox.showerror("Wrong Answer", "AI DETECTED!!!!. program closing.")
            exit(1)
        
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
            self.check_for_orders()

    
    def skip_order(self, order: Order):
        self.orders.skip_order(order)
        self.main()
    
    def check_for_orders(self):
        if self.orders.load_orders():
            self.main()

        else:
            self.clear_window()
            no_order_label = tk.Label(self.root, text="There are currently no orders.")
            no_order_label.pack()
            self.root.after(1000, self.check_for_orders)

    def clear_window(self):
        for i in self.root.winfo_children():
            i.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

