from datetime import datetime


class TimeCalculator:
    """Classe permettant de calculer le temps d'exécution entre start() et end()."""
    def __init__(self):
        self._start = None
        self._end = None

    def start(self):
        """Permet d'enregistrer le temps de début."""
        self._start = datetime.now()

    def end(self):
        """Permet d'enregistrer le temps de fin."""
        self._end = datetime.now()

    def delta(self, message = ""):
        """Permet de calculer le delta entre start et end puis l'affiche."""
        delta = self._end - self._start
        print(str(message)+" "+str(delta))
