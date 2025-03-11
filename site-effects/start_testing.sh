#!/bin/bash
python3 -m nltk.downloader stopwords

	
cd ./get_data
python3 start.py

	
cd ../analyze_data
python3 start_screenshots_analysis.py
python3 start_logs_analysis.py
cd ../