
class FileTracker:
    has_jpg_file = False
    has_pdf_file = False
    
    @classmethod
    def set_jpg(cls, value=True):
        """Set JPG file status"""
        cls.has_jpg_file = value
    
    @classmethod
    def set_pdf(cls, value=True):
        """Set PDF file status"""
        cls.has_pdf_file = value
    
    @classmethod
    def get_jpg_status(cls):
        """Get JPG file status"""
        return cls.has_jpg_file
    
    @classmethod
    def get_pdf_status(cls):
        """Get PDF file status"""
        return cls.has_pdf_file
    
    @classmethod
    def has_both_files(cls):
        """Check if both files have been uploaded"""
        return cls.has_jpg_file and cls.has_pdf_file