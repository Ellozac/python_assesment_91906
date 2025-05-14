import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import queue
import json
import os
from typing import Self
from pathlib import Path


class Order:
    """
    A class for representing customer orders

    Attr:
        order_num (int): id for the order
        items (list): A list of items in the order
        total_price (float): The total price of the order

    Methods:
        from_json(dict): creates an instance of Order from a dict and returns it
    """
    def __init__(self, order_num, items, total_price):
        """
        Initialize the order

        args:
            order_num (int): id for the order
            items (list): A list of items in the order
            total_price (float): The total price of the order 
        """
        self.order_num = order_num
        self.items = items
        self.total_price = total_price
    
    @classmethod
    def from_json(cls, json) -> Self:
        """
        Create an instance of Order from a dictionary.

        args:
            data (dict):
                'order_number' (int)
                'items' (list)
                'total_price' (float)

        returns an instance of Order
        """
        return cls(json["order_number"], [x for x in json["items"]], json["total_price"])

class OrderManager:
    """
    Manage orders which are stored in a json file an queues the orders for processing.

    Attr:
        file_path (str): Path to the json file
        queue (queue.Queue) queue object for managing order processing

    """
    def __init__(self, file_path: str = "./data/orders.json"):
        """
        initialize the order manager
        Args:
            file_path (str): path to json file
        """
        self.file_path = file_path
        self.queue = queue.Queue()
        self.load_orders()


    def load_orders(self) -> bool:
        """
        Load orders from json file to the queue
        returns:
            bool: T if orders were loaded successfully else F
        """

        # Check if the file exists
        if not os.path.exists(self.file_path):
            self.reset_json_file()
            return False
        
        # Open file with read privellidges
        with open(self.file_path, 'r') as file:
            try:
                # Load the data
                data = json.load(file)
                # Check if there is information in data and see if there are orders
                if data and len(data[0]["orders"]) > 0:
                    # Iterate the orders and append to the queue
                    for order in data[0]["orders"]:
                        self.queue.put(Order.from_json(order))
                    # Reset the orders file
                    self.reset_json_file()
                    return True
                else:
                    return False
            except ValueError:
                # see if user wants to generate a file because the data contained was not valid
                tk.messagebox.showerror(title="Error Invalid Json",message=f"Invalid JSON. {self.file_path}")
                if tk.messagebox.askyesno(title="Regenerate file?", message="Would you like to reset the file?"):
                    self.reset_json_file()
                else:
                    # Exit program with error status
                    exit(1)
            except KeyError:
                # If the json file did not contaion Orders key reset the file
                self.reset_json_file()
        return False

    def reset_json_file(self) -> None:
        """Reset the JSON file"""
        with open(self.file_path, 'w') as file:
            json.dump([{"orders": []}], file)

    def remaining_orders(self) -> int:
        """Check queue size"""
        return self.queue.qsize()

    def get_next(self) -> Order | None:
        """Get next Order"""
        if not self.queue.empty():
            return self.queue.get()
        return None

    def skip_order(self, order):
        """Move Order to back of Queue"""
        # Add the order to the end of queues
        self.queue.put(order)

class App:
    """
    Create the tkinter app

    args:
        root (tk.Tk): Main tkinter window
        file_path (str): Path to the orders json file. default './data/orders.json'
    """    

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
        self.check_robot()
        self.main()
    
    def check_robot(self):
        """Prompt user with a question to check they are not a robot"""
        ans = simpledialog.askstring("robot check", "whats 9 + 10")
        while not ans.isdigit():
            messagebox.showerror("Error", "Please only type numbers.")
            ans = simpledialog.askstring("robot check", "whats 9 + 10")
        if not int(ans) == 19:
            messagebox.showerror("Wrong Answer", "AI DETECTED!!!!. program closing.")
            exit(1)
        
    def main(self):
        """
        Main method to update the window with order detai;s
        displays info about the order to prepare and has a complete and skip button
        """

        # Check if there are orders left
        if self.orders.remaining_orders():
            # Get the next order in the queue
            order = self.orders.get_next()
            self.clear_window()
            tk.Label(self.root, text=f"Preparing order {order.order_num}").pack()
            # Display the items in the order
            for i in order.items:
                tk.Label(self.root, text=f"{i['name']} x {i['quantity']}").pack()
            
            tk.Label(self.root, text=f"Total price: ${order.total_price}").pack()

            tk.Button(self.root, text="Complete", command=self.main).pack(pady=5)
            tk.Button(self.root, text='Skip', command=lambda: self.skip_order(order)).pack(pady=5)
        else:
            # If there are no orders remaining then wait till there are new ones.
            self.check_for_orders()

    
    def skip_order(self, order: Order):
        """Skip the current order"""
        # Moves the order to the back of the queue
        self.orders.skip_order(order)
        # Redisplays main window
        self.main()
    
    def check_for_orders(self):
        """Check if there are new orders"""
        if self.orders.load_orders():
            # If there are new orders then display them
            self.main()

        else:
            self.clear_window()
            no_order_label = tk.Label(self.root, text="There are currently no orders.")
            no_order_label.pack()
            # Wait one second and then check for new orders.
            self.root.after(1000, self.check_for_orders)

    def clear_window(self):
        """Clear the main window"""
        # Iterate children of the root window
        for i in self.root.winfo_children():
            # Delete the child
            i.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

