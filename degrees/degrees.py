"""
degrees.py

This script implements a solution to the "Six Degrees of Kevin Bacon" problem,
which seeks to find the shortest path between two actors in the Hollywood film industry.
The path is defined by a series of movies that connect one actor to another.

The script utilizes a breadth-first search (BFS) algorithm to find the shortest path between two actors.
It relies on data about actors and movies, loaded from CSV files, to construct a graph where nodes represent actors,
and edges represent movies that connect two actors. The BFS algorithm explores this graph to find the shortest path
from the source actor to the target actor.

Classes:
    Node: Represents a node in the search graph, holding the state, parent, and action.
    StackFrontier: A frontier class using a stack data structure for depth-first search (unused in this script but provided for completeness).
    QueueFrontier: A frontier class using a queue data structure for breadth-first search.

Functions:
    load_data(directory): Loads people, movies, and stars data from CSV files.
    person_id_for_name(name): Finds a person's ID based on their name, handling ambiguities.
    neighbors_for_person(person_id): Finds all (movie_id, person_id) pairs representing movies the person starred in and co-stars.
    shortest_path(source_id, target_id): Implements the BFS algorithm to find the shortest path between two actors.
"""

class Node():
    """
    Node in a search graph.

    Attributes:
        state: The state of the node, representing an actor's ID in this context.
        parent: The node's parent node, representing the actor connected to this one in the previous step.
        action: The action taken to get to this node, representing the movie ID connecting this actor to the parent actor.
    """
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    """
    Stack Frontier for depth-first search.

    Attributes:
        frontier: A list representing the stack of nodes to explore.
    """
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    """
    Queue Frontier for breadth-first search.

    Inherits from StackFrontier and modifies the remove method to implement a queue.
    """
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

# Beginning implementation of degrees.py
import csv
import sys

# Assuming util.py is provided and contains these data structures
from util import Node, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.

    Args:
        directory (str): The path to the directory containing the CSV files.

    Populates the global dictionaries `names`, `people`, and `movies` with data from the CSV files.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def person_id_for_name(name):
    """
    Returns the ID for a person's name, handling cases where multiple people have the same name.

    Args:
        name (str): The name of the person to find.

    Returns:
        str: The ID of the person, or None if the person isn't found or multiple ambiguous matches exist without clarification.
    """
    name = name.lower()
    if name not in names:
        return None
    elif len(names[name]) > 1:
        print(f"Which '{name}'?")
        for person_id in names[name]:
            person = people[person_id]
            print(f"ID: {person_id}, Name: {person['name']}, Birth: {person['birth']}")
        try:
            person_id = input("Enter ID number: ")
            if person_id in names[name]:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return names[name].pop()

def neighbors_for_person(person_id):
    """
    Finds all (movie_id, person_id) pairs representing movies the person starred in and their co-stars.

    Args:
        person_id (str): The ID of the person whose neighbors are to be found.

    Returns:
        set of tuples: A set of (movie_id, person_id) tuples representing the neighbors.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

def shortest_path(source_id, target_id):
    """
    Returns the shortest path from the actor with source_id to the actor with target_id using BFS.

    Args:
        source_id (str): The ID of the source actor.
        target_id (str): The ID of the target actor.

    Returns:
        list of tuples: The shortest path as a list of (movie_id, person_id) tuples, or None if no path exists.
    """
    # Initialize the frontier with the starting position
    start = Node(state=source_id, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # Loop until the solution is found
    while True:

        # If nothing left in the frontier, then no path
        if frontier.empty():
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        explored.add(node.state)

        # Add neighbors to frontier
        for movie_id, person_id in neighbors_for_person(node.state):
            if not frontier.contains_state(person_id) and person_id not in explored:
                child = Node(state=person_id, parent=node, action=movie_id)

                # Check if the child is the goal
                if child.state == target_id:
                    # If it is, then we have found the solution
                    path = []
                    while child.parent is not None:
                        path.append((child.action, child.state))
                        child = child.parent
                    path.reverse()
                    return path

                # If not, add the new node to the frontier
                frontier.add(child)

# Main execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python degrees.py [directory]")

    directory = sys.argv[1]
    load_data(directory)

    source_name = input("Name: ")
    source_id = person_id_for_name(source_name)
    if source_id is None:
        sys.exit(f"No person with name {source_name}.")

    target_name = input("Name: ")
    target_id = person_id_for_name(target_name)
    if target_id is None:
        sys.exit(f"No person with name {target_name}.")

    path = shortest_path(source_id, target_id)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        for i, (movie_id, person_id) in enumerate(path):
            person = people[person_id]["name"]
            movie = movies[movie_id]["title"]
            print(f"{i + 1}: {person} and {person_id} starred in {movie}")
