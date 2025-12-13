from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


@dataclass
class ForensicMetadata:
    case_number: str
    examiner: str
    evidence_number: str
    acquisition_date: datetime
    system_info: Dict[str, Any]
    hash_algorithm: str
    notes: str


@dataclass
class FileMetadata:
    file_path: str
    file_name: str
    file_size: int

    modified_time: Optional[datetime]
    accessed_time: Optional[datetime]
    changed_time: Optional[datetime]
    created_time: Optional[datetime]

    md5_hash: Optional[str]
    sha1_hash: Optional[str]
    sha256_hash: Optional[str]

    file_attributes: List[str]
    alternate_data_streams: List[str]

    owner: Optional[str]
    permissions: Optional[str]


class ForensicFormats:
    DISK_IMAGE_FORMATS = {
        'dd': '.dd',
        'e01': '.E01',
        'aff': '.aff',
        'aff4': '.aff4',
    }

    MEMORY_FORMATS = {
        'raw': '.raw',
        'lime': '.lime',
        'dmp': '.dmp',
    }

    NETWORK_FORMATS = {
        'pcap': '.pcap',
        'pcapng': '.pcapng',
    }

    TIMELINE_FORMATS = {
        'csv': '.csv',
        'json': '.json',
        'bodyfile': '.body',
    }


class BodyFileFormat:
    @staticmethod
    def generate_entry(file_meta: FileMetadata) -> str:
        md5 = file_meta.md5_hash or "0"

        name = file_meta.file_path

        inode = "0"

        mode = "0"

        uid = "0"
        gid = "0"

        # Size
        size = str(file_meta.file_size)

        def to_timestamp(dt: Optional[datetime]) -> str:
            if dt:
                return str(int(dt.timestamp()))
            return "0"

        atime = to_timestamp(file_meta.accessed_time)
        mtime = to_timestamp(file_meta.modified_time)
        ctime = to_timestamp(file_meta.changed_time)
        crtime = to_timestamp(file_meta.created_time)

        return f"{md5}|{name}|{inode}|{mode}|{uid}|{gid}|{size}|{atime}|{mtime}|{ctime}|{crtime}"


class DFXMLGenerator:
    @staticmethod
    def generate_header(metadata: ForensicMetadata) -> str:
        return f"""<?xml version='1.0' encoding='UTF-8'?>
                <dfxml version='1.2.0'
                    xmlns='http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML'
                    xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
                    xmlns:dc='http://purl.org/dc/elements/1.1/'>
                <metadata>
                    <dc:type>Forensic Evidence Collection</dc:type>
                    <case_number>{metadata.case_number}</case_number>
                    <examiner>{metadata.examiner}</examiner>
                    <evidence_number>{metadata.evidence_number}</evidence_number>
                    <acquisition_date>{metadata.acquisition_date.isoformat()}</acquisition_date>
                </metadata>
                <creator>
                    <program>WinScope Evidence Collection Tool</program>
                    <version>0.1.0</version>
                </creator>
                <source>
                    <image_type>logical</image_type>
                </source>
                """

    @staticmethod
    def generate_file_object(file_meta: FileMetadata) -> str:
        return f"""  <fileobject>
            <filename>{file_meta.file_name}</filename>
            <filesize>{file_meta.file_size}</filesize>
            <alloc>1</alloc>
            <used>1</used>
            <mtime>{file_meta.modified_time.isoformat() if file_meta.modified_time else ''}</mtime>
            <atime>{file_meta.accessed_time.isoformat() if file_meta.accessed_time else ''}</atime>
            <ctime>{file_meta.changed_time.isoformat() if file_meta.changed_time else ''}</ctime>
            <crtime>{file_meta.created_time.isoformat() if file_meta.created_time else ''}</crtime>
            <hashdigest type='md5'>{file_meta.md5_hash or ''}</hashdigest>
            <hashdigest type='sha1'>{file_meta.sha1_hash or ''}</hashdigest>
            <hashdigest type='sha256'>{file_meta.sha256_hash or ''}</hashdigest>
        </fileobject>
        """

    @staticmethod
    def generate_footer() -> str:
        return "</dfxml>"


class CaseManagement:
    @staticmethod
    def create_case_info() -> Dict[str, Any]:
        from datetime import datetime
        import socket
        import getpass

        return {
            'case_number': input("Enter Case Number (or press Enter for auto): ").strip() or f"CASE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'examiner': input("Enter Examiner Name: ").strip() or getpass.getuser(),
            'evidence_number': input("Enter Evidence Number (or press Enter for auto): ").strip() or f"EVID-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'incident_date': input("Enter Incident Date (YYYY-MM-DD) or press Enter for today: ").strip() or datetime.now().strftime('%Y-%m-%d'),
            'description': input("Enter Case Description: ").strip() or "Evidence collection from target system",
            'location': input("Enter Evidence Location: ").strip() or socket.gethostname(),
        }
