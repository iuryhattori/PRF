from src.extractor.xml_to_csv import xml_folder_to_csv


if __name__ == "__main__":
    df = xml_folder_to_csv("Sintetic_Xml", "csv/ctes.csv")
    print(df.head())