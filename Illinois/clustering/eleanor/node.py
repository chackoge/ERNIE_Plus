from collections import Counter
import copy

class Node():
   def __init__(self, set_label):
       self.label=set_label
       self.in_degree=0
       self.out_degree=0
       self.in_neighbors=Counter()
       self.out_neighbors=Counter()

       self.save_in_degree=0
       self.save_out_degree=0
       self.save_in_neighbors=Counter()
       self.save_out_neighbors=Counter()  

   def add_in_degree(self, node):
       self.in_degree += 1
       self.in_neighbors.update([node])

   def add_out_degree(self, node):
       self.out_degree += 1
       self.out_neighbors.update([node])

   def get_label(self):
       return self.label

   def get_out_degree(self):
       return self.out_degree

   def get_in_degree(self):
       return self.in_degree

   def get_degree(self):
       return self.in_degree + self.out_degree

   def get_out_neighbors(self):
       return self.out_neighbors

   def get_in_neighbors(self):
       return self.in_neighbors

   def get_neighbors(self):
       return set(self.in_neighbors).union(set(self.out_neighbors))

   def remove_in_degree(self, node):
       self.in_degree -= self.in_neighbors[node]
       del self.in_neighbors[node]

   def remove_out_degree(self, node):
       self.out_degree -= self.out_neighbors[node]
       del self.out_neighbors[node]

   def remove_edges(self, node):
       if node in self.in_neighbors:
           self.remove_in_degree(node)
       if node in self.out_neighbors:
           self.remove_out_degree(node)

   def reset_node(self):
       self.in_neighbors = Counter()
       self.in_neighbors.update(self.save_in_neighbors)
       self.out_neighbors = Counter()
       self.out_neighbors.update(self.save_out_neighbors)

       self.in_degree = self.save_in_degree
       self.out_degree = self.save_out_degree

   def save_node(self):
       self.save_in_neighbors = Counter()
       self.save_in_neighbors.update(self.in_neighbors)
       self.save_out_neighbors = Counter()       
       self.save_out_neighbors.update(self.out_neighbors)
       
       self.save_in_degree = self.in_degree
       self.save_out_degree = self.out_degree


class Component():
    def __init__ (self, seed_node):
        self.node_dict = {seed_node.get_label() : seed_node}
        self.size = 1
        self.min_degree = seed_node.get_degree()
        
    def update(self, node):
        if node.get_label() not in self.node_dict:
            self.size += 1
        self.node_dict[node.get_label()] = node
        if node.get_degree() < self.min_degree:
            self.min_degree = node.get_degree()
            
    def get_size(self):
        return self.size
        
    def get_node_dict(self):
        return self.node_dict
        
    def get_min_degree(self):
        return self.min_degree
