# FIKSE:
# Endre til relative imports "."
# Lage metode som flytter dyr mellom celler.
# Lage metode som fjerner dyr (ved død).
# Annual cycle
# I annual cycle methods: sorter animals først i alle.
# lognormvariate: bruk egen funksjon. [i procreate()]
# Cell reset fodder.



import textwrap
import numpy as np
import pandas as pd
import math as m
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

from src.biosim.animals import Herbivore, Carnivore

class Island:
    def __init__(self, geography, ini_pop=None):
        self.geography = geography
        self.terrain, self.coordinates = self.terraform()

        # Runs add_population if ini_pop is not None:
        self.add_population(population=ini_pop) if ini_pop is not None else None

    def lognormv(self):
        """
        a continuous probability distribution of a random variable whose
        logarithm is normally distributed

        Used to draw birth weights
        """

        w_birth=self.w_birth
        sigma_birth=self.sigma_birth


        mu=m.log((w_birth**2)/m.sqrt(sigma_birth**2+w_birth**2))
        sigma=m.sqrt(m.log(1+((sigma_birth**2)/(w_birth**2))))
        return random.lognormvariate(mu,sigma)


    def add_population(self, population):
        """
        Adds a population to the island.

        Parameters
        ----------
        - population: list of dictionaries.
            [{"loc": (x, y), "pop": [{"species": val, "age": val, "weight": val}]}]

        Raises
        ------
        - ValueError
            If the location is not on the map.
            If the location is in Water ("W").
            If the animal is invalid.
        """

        for animals in population:
            location = animals["loc"]
            if location not in self.coordinates:
                raise ValueError("Invalid location: {0}".format(location))
            if self.terrain[location[0]-1][location[1]-1] == "W":
                raise ValueError("Animals cannot be placed in water (location: {0}).".format(
                    location))
            for animal in animals["pop"]:
                if "age" not in animal:
                    animal["age"] = None
                if "weight" not in animal:
                    animal["weight"] = None
                try:
                    self.cells[location[0]-1][location[1]-1].add_animal(species=animal["species"],
                                                                        age=animal["age"],
                                                                        weight=animal["weight"])

                except:
                    raise ValueError("Error when adding: {0}".format(animal))

    @property
    def n_animals(self):
        """
        Counts the number of animals on the island.

        Returns
        -------
        - n_herbivores: dictionary
            {"Herbivores": n_herbivores, "Carnivores": n_carnivores}
        """

        n_animals = {"Herbivores": 0, "Carnivores": 0}
        for cells in self.cells:
            for cell in cells:
                n_animals["Herbivores"] += len(cell.animals["Herbivores"])
                n_animals["Carnivores"] += len(cell.animals["Carnivores"])
        return n_animals

    def terraform(self):
        """
        Creates a terrain from a given geography.
        Visualises the map if specified.

        Parameters
        ----------
        - geography: str
            A string representing the geography of the island.
        - visualise: bool
            A boolean representing whether or not the map should be visualised.

        Raises
        ------
        - ValueError
            If the edges of the map are not "W" (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.

        Returns
        -------
        - terrain: list of strings
            A list of strings representing the terrain of the island.
        - coordinates: list
            A list representing the coordinates of the island. Each letter in the terrain
            corresponds to its own cell.
            The top left corner has the coordinates (1, 1).
        """

        island = textwrap.dedent(self.geography)
        terrain = island.split("\n")
        X = len(terrain)
        Y = len(terrain[0])

        # Checks whether the map is rectangular:
        for i in range(X):
            if len(terrain[i]) != Y:
                raise ValueError("The map must be rectangular.")

        # Checks whether the edges are "W" (Water):
        for i in range(X):
            if terrain[i][0] != "W" or terrain[i][Y-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(Y):
            if terrain[0][j] != "W" or terrain[X-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

        # Checks whether the map contains only valid characters:
        for i in range(X):
            for j in range(Y):
                if terrain[i][j] not in ["W", "L", "H", "D"]:
                    raise ValueError("Cell {0} contains an invalid letter ({1}).".format((i+1, j+1),
                                                                                         terrain[i][j]))

        # Creates the coordinate-map:
        self.cells = []
        coordinates = []
        for i in range(X):
            row = []
            for j in range(Y):
                row.append(Cell())
                coordinates.append((i+1, j+1))
            self.cells.append(row)

        return terrain, coordinates

    def visualise(self, colours=None):
        """
        Visualises the island.

        Parameters
        ----------
        - colours: dict
            {"Type": [R, G, B]}
            A dictionary containing the colours of the different terrains.
            Must contain types: "W", "L", "H" and "D".
                If "None", the default colours will be used.
        """

        # Defining colours:
        if type(colours) is not dict:  # Using default colours if not otherwise specified.
            colours = {
                "L": [185, 214, 135],
                "H": [232, 236, 158],
                "D": [255, 238, 186],
                "W": [149, 203, 204]
            }

        X = len(self.terrain)
        Y = len(self.terrain[0])
        coloured_map = np.empty((X, Y, 3), dtype="uint8")

        # Inserting colours into the island:
        for i in range(X):
            for j in range(Y):
                if self.terrain[i][j] == "W":
                    coloured_map[i, j] = colours["W"]
                elif self.terrain[i][j] == "L":
                    coloured_map[i, j] = colours["L"]
                elif self.terrain[i][j] == "H":
                    coloured_map[i, j] = colours["H"]
                elif self.terrain[i][j] == "D":
                    coloured_map[i, j] = colours["D"]

        # Visualising the island:
        plt.imshow(coloured_map)
        plt.xticks([]), plt.yticks([]), plt.title("Map of Pylandia")

        description = {"L": "Lowland", "H": "Highland", "D": "Desert", "W": "Water"}
        patches = [mpatches.Patch(color=(val[0] / 255, val[1] / 255, val[2] / 255),
                                  label="{0}".format(
                                      str(pd.DataFrame([key]).replace(description)[0][0]))) for
                   key, val in colours.items()]
        plt.legend(handles=patches, bbox_to_anchor=(0, -0.01), loc=2, borderaxespad=0)

        plt.show()

    def procreate(self):
        """
        Iterates through all the animals on the island.
        An animal gives birth to a baby if the following conditions are met:
        - A probability of min(1, gamma * fitness * N).
        - The baby's weight is less than the parent's weight.
        If a baby is born, it is added to the cell of the parent.
        """

        N = self.n_animals
        for cells in self.cells:
            for cell in cells:
                if cell.animals["Herbivores"] or cell.animals["Carnivores"]:
                    for animal in cell.animals["Herbivores"] + cell.animals["Carnivores"]:
                        if random.random > min(1, animal.gamma * animal.fitness * N):
                            return
                        baby_weight = lognormv(self)
                        if baby_weight > animal.w:
                            return
                        cell.add_animal(species=animal.species, age=0, weight=baby_weight)

    def feed(self):
        for cells in self.cells:
            for cell in cells:
                if cell.animals["Herbivores"] or cell.animals["Carnivores"]:
                    cell.reset_fodder()
                    for herbivore in cell.animals["Herbivores"]:
                        pass
                    for carnivore in cell.animals["Carnivores"]:
                        pass

    def migrate(self):
        pass

    def aging(self):
        pass

    def weight_loss(self):
        pass

    def death(self):
        pass

    def yearly_cycle(self):
        # All animals undergo steps simultaneously.

        # 1. Procreation

        self.procreate()

        # 2. Feeding

        self.feed()

        # 3. Migration

        self.migrate()

        # 4. Aging

        self.aging()

        # 5. Weight loss

        self.weight_loss()

        # 6. Death

        self.death()

class Cell:

    def __init__(self):
        self.animals = {"Herbivores": [], "Carnivores": []}

    def add_animal(self, species, age=None, weight=None):
        """
        Adds an animal to the cell.

        Parameters
        ----------
        - species: str
            A string representing the species of the animal.
        - age: int
            An integer representing the age of the animal.
        - weight: float
            A float representing the weight of the animal.

        Raises
        ------
        - ValueError
            If the species is not "Herbivore" or "Carnivore".
        """

        if species not in ["Herbivore", "Carnivore"]:
            raise ValueError("The species must be either 'Herbivore' or 'Carnivore'.")
        if species == "Herbivore":
            self.animals["Herbivores"].append(Herbivore(age=age, weight=weight))
        else:
            self.animals["Carnivores"].append(Carnivore(age=age, weight=weight))

    def reset_fodder(self):
        """
        Resets the amount of fodder in the cell.
        """

        self.fodder = 0

if __name__ == "__main__":
    geogr = """\
                   WWWWWWWWWWWWWWWWWWWWW
                   WHWWWWWWHWWWWLLLLLLLW
                   WHHHHHLLLLWWLLLLLLLWW
                   WHHHHHHHHHWWLLLLLLWWW
                   WHHHHHLLLLLLLLLLLLWWW
                   WHHHHHLLLDDLLLHLLLWWW
                   WHHLLLLLDDDLLLHHHHWWW
                   WWHHHHLLLDDLLLHWWWWWW
                   WHHHLLLLLDDLLLLLLLWWW
                   WHHHHLLLLDDLLLLWWWWWW
                   WWHHHHLLLLLLLLWWWWWWW
                   WWWHHHHLLLLLLLWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWW"""

    a = Island(geogr)

    new_animals = [{"loc": (2, 2),
                    "pop": [{"species": "Herbivore"}]}]
    a.add_population(new_animals)

    print(a.cells[1][1].animals["Herbivores"][0].w)

    print(a.n_animals)

    new_animal = [{"loc": (2, 2),
                    "pop": [{"species": "Herbivore"}]}]
    a.add_population(new_animal)
    print(a.n_animals)