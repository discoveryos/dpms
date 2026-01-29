import os
from typing import Dict, Any, Optional, List
from dpms.dpms_frontend import print_error 

# --- Configuration ---
# The single index file in the mirror repository that lists all packages
PACKAGE_INDEX_FILENAME = "packages.txt" 
REQUIRED_FIELDS = ['name', 'version', 'source_url', 'dependencies', 'build_steps']

class PackageReader:
    """
    Reads and validates the central package index file (packages.txt) 
    from a local mirror clone.
    """

    def _init_(self, mirror_path: str):
        """
        Initializes the reader with the local path to the cloned mirror directory.
        """
        self.mirror_path = mirror_path
        self.index_file = os.path.join(mirror_path, PACKAGE_INDEX_FILENAME)
        
    def _load_index(self) -> Optional[List[Dict[str, Any]]]:
        """
        Loads and parses the text index file.
        Each line is expected to be a comma-separated list of package data.
        """
        if not os.path.exists(self.index_file):
            print_error(f"Index file not found in local path: {self.index_file}")
            return None
        
        package_list = []
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Split line into fields
                    fields = [f.strip() for f in line.split(',')]
                    
                    if len(fields) != len(REQUIRED_FIELDS):
                        print_error(f"Skipping malformed line in index (expected {len(REQUIRED_FIELDS)} fields): {line}")
                        continue
                        
                    # Map fields to a dictionary
                    package_data = dict(zip(REQUIRED_FIELDS, fields))
                    
                    # Process dependencies: convert comma-separated string to dict
                    dependencies_dict = {}
                    dependencies_str = package_data.pop('dependencies') # Get the string and remove from main dict
                    
                    for dep in dependencies_str.split('|'): # Assuming pipe (|) separates dependencies in the string
                        dep = dep.strip()
                        if dep:
                            # Simple dependency mapping: e.g., "zlib" -> "latest"
                            dependencies_dict[dep] = 'latest' 
                            
                    package_data['dependencies'] = dependencies_dict
                    
                    package_list.append(package_data)
                        
            return package_list
            
        except Exception as e:
            print_error(f"Failed to read index file: {e}")
            return None

    def get_all_packages(self) -> Optional[List[Dict[str, Any]]]:
        """
        Returns a list of all packages found in the index, or None if reading fails.
        """
        return self._load_index()

# --- Example packages.txt content (Conceptual) ---
# Each line is: name, version, source_url, dependencies, build_steps
# Note: Dependencies are separated by | in this example for parsing simplicity.
#
# my-app,1.0.0,https://github.com/user/my-app.git,zlib|openssl,cmake|make|make install
# another-tool,2.5,https://gitlab.com/repo/tool.git,libc,gcc|make
