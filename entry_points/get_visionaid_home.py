from vision_aid.ingestion.pull_html import download_html

if __name__=='__main__':
    download_html("https://visionaid.org/",filename="test_html.txt")