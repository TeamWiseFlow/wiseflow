import pandas as pd
from typing import List, Dict, Optional, Union
from pathlib import Path
from .pb_api import PbTalker
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
print(".env is loc in:", Path(__file__).parent.parent.parent)
if env_path.exists():
    load_dotenv(env_path)

class PbExporter(PbTalker):
    def __init__(self, logger) -> None:
        super().__init__(logger)

    def export_to_csv(self, 
                     collection_name: str,
                     output_path: Union[str, Path],
                     fields: Optional[List[str]] = None,
                     filter_str: str = '',
                     preprocess_func = None) -> bool:
        """
        Export collection data to CSV file
        
        Args:
            collection_name: PocketBase collection name
            output_path: Path to save the CSV file
            fields: List of fields to export
            filter_str: Filter string for PocketBase query
            preprocess_func: Optional function to process data before export
        """
        try:
            # Get data from PocketBase
            data = self.read(
                collection_name=collection_name,
                fields=fields,
                filter=filter_str
            )
            
            # Apply preprocessing if provided
            if preprocess_func and callable(preprocess_func):
                data = preprocess_func(data)

            # Convert to DataFrame and export with UTF-8 encoding
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')  # 使用 utf-8-sig 来支持 Excel 打开
            
            self.logger.info(f"Successfully exported {len(data)} records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            return False

    def export_to_excel(self,
                       collection_name: str,
                       output_path: Union[str, Path],
                       fields: Optional[List[str]] = None,
                       filter_str: str = '',
                       preprocess_func = None,
                       sheet_name: str = 'Sheet1') -> bool:
        """
        Export collection data to Excel file
        
        Args:
            collection_name: PocketBase collection name
            output_path: Path to save the Excel file
            fields: List of fields to export
            filter_str: Filter string for PocketBase query
            preprocess_func: Optional function to process data before export
            sheet_name: Name of the Excel sheet
        """
        try:
            # Get data from PocketBase
            data = self.read(
                collection_name=collection_name,
                fields=fields,
                filter=filter_str
            )

            # Apply preprocessing if provided
            if preprocess_func and callable(preprocess_func):
                data = preprocess_func(data)

            # Convert to DataFrame and export
            df = pd.DataFrame(data)
            df.to_excel(output_path, sheet_name=sheet_name, index=False)
            
            self.logger.info(f"Successfully exported {len(data)} records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            return False
