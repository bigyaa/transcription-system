# Isc Transcription

## Description
The inception of this project was driven by the International Storytelling Center's imperative need to transcribe and catalog its extensive audio file collection efficiently. Recognizing the manual transcription process as time-consuming and tedious, the project initially focused on leveraging the power of Whisper, an advanced Open AI technology, to automate the transcription and diarization of audio files with exceptional accuracy.

Now, the project has evolved into a versatile application accessible to anyone seeking a streamlined solution for transcribing and diarizing their audio files. Utilizing the robust capabilities of Whisper, this Python-based tool empowers users to effortlessly convert their audio files into text format, offering a time-efficient and resource-saving alternative for individuals, organizations, and cultural institutions alike. The democratization of this technology ensures that the benefits extend beyond the initial motive, providing a valuable and accessible resource for diverse transcription needs.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Installation

1. Clone the repository:
```bash 
git clone https://github.com/rubenmaharjan/isc-transcription.git
```
2. Navigate to the cloned directory:
```bash 
cd isc-transcription
```
3. Install the required packages:
```bash 
pip install -r requirements.txt
```
4. Run the program:
```bash 
python main.py
```
## Usage
To run the transcription process, follow these steps:

1. Open a terminal and navigate to the project directory.

2. Make sure you have activated the virtual environment (if you are using one).

3. Run the following command to start the transcription process:
```bash
python main.py
```
This will run the transcription process based on the configuration that has been created.

4. Once the process is complete, the transcribed text will be saved to a text file in the output directory.

Note: Make sure to update the configuration file (config.xml) with the correct settings before running the code. You can also specify the audio files you want to transcribe by adding their file paths to the audio_files list in main.py.

If you encounter any issues or have any questions, please refer to the Contributing Guidelines or contact the project maintainers.


## Acknowledgements
We would like to express our gratitude to the following individuals and organizations who contributed to this project:

- Phil Pfeiffer, who provided valuable feedback and testing for the code.
- The International Storytelling Center, who provided the audio files used in the project.
- OpenAI, who developed the Whisper tool used for transcription.
- The Python community, for their invaluable resources and support.

Thank you all for your help and support!
