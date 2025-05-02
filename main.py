import tkinter as tk
import queue
import json
import os

class QueueManager(queue.Queue):
    def __init__(self, file_path="orders.json"):
        super().__init__()
        self.file_path = file_path
        self.json_to_queue()

    def json_to_queue(self) -> bool:
        if not os.path.exists(self.file_path):
            self.reset_json_file()
            return False

        with open(self.file_path, 'r')as file:
            try:
                data = json.load(file)
                if data and "orders" in data[0]:
                    for order in data[0]["orders"]:
                        self.put(order)
                    self.reset_json_file()
                    return True
                    
            except json.JSONDecodeError:
                print("Invalid Json. resetting file.")
                self.reset_json_file()
        return False

    def reset_json_file(self):
        with open(self.file_path, 'w') as file:
            json.dump([], file)


    def remaining_orders(self):
        return self.qsize()


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Order to Prepare") 
        self.orders = QueueManager()
        self.main()
    
    def main(self):
        if self.orders.remaining_orders():
            order = self.orders.get()
            self.clear_window()
            tk.Label(self.root, text=f"Preparing order {order['order_number']}").pack()
            for i in order['items']:
                label = tk.Label(self.root, text=f"{i['name']} x {i['quantity']}")
                label.pack()
            tk.Label(self.root, text=f"Total price: ${order['total_price']}").pack()
            tk.Button(self.root, text="Complete", command=self.main).pack(pady=5)
            tk.Button(self.root, text='Skip', command=lambda: self.skip_order(order)).pack(pady=5)

        else:
            self.clear_window()
            x = tk.Label(self.root, text="There are currently no orders.")
            x.pack()
            self.root.after(1000, self.check_for_orders)

    def skip_order(self, order):
        self.orders.put(order)
        self.main()

    def check_for_orders(self):
        if self.orders.json_to_queue():
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

