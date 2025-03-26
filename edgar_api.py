import requests
import time
import json

class SECFilingRetriever:
    def __init__(self):
        # Required SEC.gov header
        self.headers = {
            "User-Agent": "Exploratory Analysis of 10-Q for SBA Lenders (your-email@example.com)",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        # SEC rate limiting - 10 requests per second
        self.request_delay = 0.1
    
    def get_latest_filing(self, cik, form_type="10-Q"):
        """
        Get the latest filing of specified type for a company
        
        Parameters:
        - cik: Company CIK number (string)
        - form_type: Filing type to retrieve (default: "10-Q")
        
        Returns:
        - Dictionary with filing information or None if not found
        """
        # Pad CIK to 10 digits as required by SEC API
        padded_cik = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{padded_cik}.json"
        
        try:
            # Make API request
            response = requests.get(url, headers=self.headers)
            time.sleep(self.request_delay)  # Respect rate limits
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for the specified form type
                for i, form in enumerate(data["filings"]["recent"]["form"]):
                    if form == form_type:
                        # Extract filing details
                        accession_number = data["filings"]["recent"]["accessionNumber"][i]
                        filing_date = data["filings"]["recent"]["filingDate"][i]
                        primary_doc = data["filings"]["recent"]["primaryDocument"][i]
                        
                        # Clean accession number (remove dashes)
                        accession_clean = accession_number.replace("-", "")
                        
                        # Construct URLs
                        document_url = f"https://www.sec.gov/ix?doc=/Archives/edgar/data/{int(cik)}/{accession_clean}/{primary_doc}"
                        raw_filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{primary_doc}"
                        
                        # Return filing information
                        return {
                            "cik": cik,
                            "company_name": data["name"],
                            "form_type": form_type,
                            "filing_date": filing_date,
                            "accession_number": accession_number,
                            "document_url": document_url,
                            "raw_filing_url": raw_filing_url,
                            "primary_document": primary_doc
                        }
                
                # If we get here, the form type wasn't found
                print(f"No {form_type} filing found for CIK {cik}")
                return None
            else:
                print(f"API request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error retrieving filing: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    retriever = SECFilingRetriever()
    
    # Example: Get the latest 10-Q for Live Oak Bancshares
    result = retriever.get_latest_filing("0001462120")
    
    if result:
        print(f"Latest {result['form_type']} filing for {result['company_name']}:")
        print(f"Filing Date: {result['filing_date']}")
        print(f"Document URL: {result['document_url']}")
        print(f"Raw Filing URL: {result['raw_filing_url']}")