from abc import ABC, abstractmethod


class Transcribe(ABC):
    """
           A class to represent the type of Transcription model chosen for transcription.
           e.g. Whisper, DeepSeepch and so on.

           ...

           Attributes
           ----------

           Methods
           -------
           setup() : Setup up the chose model with the configuration 

           transcribe(): Start the transcription and store it in a file.
    """

    @abstractmethod
    def setup(self):
        """
        Creates the class with initial values assigned

        Returns
        -------
        self

        """

    @abstractmethod
    def transcribe(self):
        """
        Transcribes and stores in the file.

        Returns
        -------
        self

        """
