import importlib
import subprocess
import sys
import os

def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)

def check_import(module_name, required_version=None):
    """Check if a module can be imported and verify its version if required."""
    try:
        # Handle special cases for package names that differ from import names
        import_name = module_name
        if module_name == "beautifulsoup4":
            import_name = "bs4"
        
        # Use pip to get the version
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", module_name],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f"{module_name:<20} {'N/A':<10} ✗ NOT INSTALLED")
            return False
            
        # Parse the version from pip show output
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        if not version_line:
            installed_version = "Unknown"
        else:
            installed_version = version_line[0].split(':', 1)[1].strip()
        
        # Try to import the module to verify it works
        importlib.import_module(import_name)
        
        status = "✓ INSTALLED"
        if required_version and installed_version != required_version:
            status = f"⚠ VERSION MISMATCH (found {installed_version}, need {required_version})"
        print(f"{module_name:<20} {installed_version:<10} {status}")
        return True
    except ImportError as e:
        print(f"{module_name:<20} {'ERROR':<10} ✗ IMPORT ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"{module_name:<20} {'ERROR':<10} ✗ {str(e)}")
        return False

def check_compatibility():
    """Check if the installed libraries work together without issues."""
    print_section("COMPATIBILITY TEST")
    
    try:
        # Test numpy and pandas compatibility
        import numpy as np
        import pandas as pd
        
        # Create a simple DataFrame
        df = pd.DataFrame({'A': np.array([1, 2, 3])})
        print("numpy + pandas: ✓ COMPATIBLE")
        
        # Test BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<p>Test</p>", "html.parser")
        print("beautifulsoup4: ✓ WORKING")
        
        return True
    except Exception as e:
        print(f"Package compatibility issue: ✗ INCOMPATIBLE - {str(e)}")
        return False

def check_directories():
    """Check if required directories exist, create them if not."""
    print_section("DIRECTORY STRUCTURE")
    
    base_dir = "baseball_data"
    subdirs = ["final", "yearly", "archive", "tests"]
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created: {base_dir}/")
    else:
        print(f"Exists:  {base_dir}/")
    
    for subdir in subdirs:
        path = os.path.join(base_dir, subdir)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created: {path}/")
        else:
            print(f"Exists:  {path}/")

def install_missing(missing_packages):
    """Attempt to install missing packages."""
    print_section("INSTALLING MISSING PACKAGES")
    
    for package in missing_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}.")

def main():
    print_section("ENVIRONMENT CHECK")
    print(f"Python version: {sys.version}")
    
    print_section("REQUIRED PACKAGES")
    print(f"{'Package':<20} {'Version':<10} {'Status'}")
    print("-" * 50)
    
    # List of required packages
    required_packages = {
        "requests": None,
        "beautifulsoup4": None,
        "pandas": None,
        "numpy": None,
        "lxml": None,
    }
    
    missing_packages = []
    
    for package, req_version in required_packages.items():
        if not check_import(package, req_version):
            missing_packages.append(package)
    
    if missing_packages:
        response = input("\nWould you like to install missing packages? (y/n): ")
        if response.lower() == 'y':
            install_missing(missing_packages)
            # Recheck after installation
            print_section("RECHECKING PACKAGES")
            print(f"{'Package':<20} {'Version':<10} {'Status'}")
            print("-" * 50)
            still_missing = []
            for package in missing_packages:
                if not check_import(package):
                    still_missing.append(package)
            missing_packages = still_missing
    
    # Check compatibility only if no packages are missing after potential installation
    if not missing_packages:
        compatibility_ok = check_compatibility()
    else:
        print("\nSkipping compatibility check due to missing packages.")
        compatibility_ok = False
    
    # Check and create directories
    check_directories()
    
    # Final status
    print_section("SUMMARY")
    if missing_packages:
        print("✗ Some required packages are missing.")
        print("Please install them manually or run this script again.")
    elif not compatibility_ok:
        print("✗ Package compatibility issues detected.")
        print("Try reinstalling the packages with compatible versions:")
        print("pip uninstall -y numpy pandas && pip install numpy==1.24.3 pandas==2.0.3")
    else:
        print("✓ All checks passed! Your environment is ready for the baseball scraper.")
        print("Run the scraper with: python scrape_full_dataset_v2.py")

if __name__ == "__main__":
    main() 