"""
This is a small demo script running BioSim with the Graphical User Interface (GUI).
"""

from src.biosim.gui import BioSimGUI

if __name__ == "__main__":

    _MAP_SIZE = 20

    BioSimGUI(map_size=_MAP_SIZE).mainloop()
