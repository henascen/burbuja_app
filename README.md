# Burbuja App

This app lets you create a pdf with ready-to-print test templates. After the test sheets are answered by the examinees the app allows you to upload the picture of each test and grade them automatically by comparing them to previusly uploaded answer sheet. It aims to be a tool for teachers and examiners that are interested in accessing great tools to improve their effiency and focus their time in more demanding tasks.

The type of tests targeted by this apps are standardized tests. These are a good resourse in the right environments, it allows the reuse of the sheets if they are laminated for different questions and answers options and are relative easy to analyze using computer vision

- The base template supported by the app is the following: 

![](/resources/images/base_format.png)

*Currently the app only supports grading tests that include 40 questions for scale.*

## The Burbuja app interface:
- **The main menu**

![](/resources/images/main_window.png)

- **The grade tests menu**

![](/resources/images/multiplegrading_allgraded.png)

- **The create test sheets window**

![](/resources/images/template_creation.png)

- **An example of an answer sheet read by the app**

![](/resources/images/encontrado_marcada10_eng.jpg)

- **An example of a solved test before processing**

![](/resources/images/grayscale_eng.jpg)

- **Example of the result after processing and grading the solved test**

![](/resources/images/gradint_one_test.png)

- **The results window**

![](/resources/images/results_window.png)

## Requirements:
- Python 3.6.X
- Install Tesseract OCR in your computer -> ([Here's](https://www.pyimagesearch.com/2017/07/03/installing-tesseract-for-ocr/) a nice guide)
- Install requirements.txt with pip

### Ready-to-use versions availabe:
- Soon

### Disclaimer
- The code was written with variables and references in spanish because the development was done to be as easier to read as possible for educational purposes. 
