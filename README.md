# Python Web Scraper for Job Listings

This project is a web scraper designed to extract job listings from the 104 Job Bank website. It specifically targets positions that require less than one year of experience, are posted today, and require candidates with a master's degree or lower. The results are outputted to an Excel file for easy viewing and analysis.

## Project Structure

```
python-web-scraper
├── src
│   ├── scraper.py        # Main logic for the web scraper
│   └── utils
│       └── __init__.py   # Utility functions for the scraper
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd python-web-scraper
   ```

2. **Install the required dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the scraper, execute the following command:
```
python src/scraper.py
```

The scraper will fetch job listings based on the specified criteria and save the results to an Excel file in the project directory.

## Dependencies

This project requires the following Python libraries:
- `requests`: For making HTTP requests to the job listings website.
- `BeautifulSoup`: For parsing HTML and extracting job listing data.
- `pandas`: For data manipulation and exporting the results to an Excel file.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.