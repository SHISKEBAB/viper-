#!/usr/bin/env python3
"""
VIPER System Launch Status Report
Final validation that the system is ready for launch
"""

import subprocess
import sys
from pathlib import Path

def check_critical_files():
    """Check that all critical launch files exist and have valid syntax"""
    print("📁 Checking Critical Launch Files...")
    
    critical_files = [
        'launch_viper.py',
        'start_trading.py', 
        'scripts/launch_integrated_system.py',
        'scripts/launch_complete_system.py',
        'src/viper/execution/final_live_trading_launcher.py',
        'docker-compose.yml',
        '.env.example'
    ]
    
    all_good = True
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            
            # Test Python files for syntax
            if file_path.endswith('.py'):
                try:
                    result = subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                                          capture_output=True)
                    if result.returncode != 0:
                        print(f"   ❌ {file_path}: Syntax error")
                        all_good = False
                except Exception:
                    print(f"   ⚠️  {file_path}: Could not test syntax")
                    
        else:
            print(f"   ❌ {file_path}: Missing")
            all_good = False
            
    return all_good

def check_dependencies():
    """Check that critical Python dependencies are available"""
    print("\n📦 Checking Python Dependencies...")
    
    critical_deps = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'numpy',
        'ccxt',
        'redis',
        'requests',
        'dotenv'  # python-dotenv imports as 'dotenv'
    ]
    
    all_good = True
    for dep in critical_deps:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {dep.replace("-", "_")}'], 
                                  capture_output=True)
            if result.returncode == 0:
                print(f"   ✅ {dep}")
            else:
                print(f"   ❌ {dep}: Not available")
                all_good = False
        except Exception:
            print(f"   ❌ {dep}: Import failed")
            all_good = False
            
    return all_good

def check_docker():
    """Check Docker availability"""
    print("\n🐳 Checking Docker...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Docker: {result.stdout.strip()}")
            
            # Check docker-compose
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Docker Compose: Available")
                return True
            else:
                print(f"   ❌ Docker Compose: Not available")
                return False
        else:
            print(f"   ❌ Docker: Not available")
            return False
    except Exception:
        print(f"   ❌ Docker: Not installed")
        return False

def main():
    """Main status check"""
    print("🚀 VIPER SYSTEM LAUNCH STATUS REPORT")
    print("="*60)
    
    files_ok = check_critical_files()
    deps_ok = check_dependencies() 
    docker_ok = check_docker()
    
    print("\n" + "="*60)
    print("📊 FINAL STATUS REPORT")
    print(f"   Critical Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    print(f"   Dependencies:   {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"   Docker:         {'✅ PASS' if docker_ok else '❌ FAIL'}")
    
    if files_ok and deps_ok and docker_ok:
        print("\n🎉 SYSTEM IS READY FOR LAUNCH!")
        print("🚀 You can now start the VIPER trading system using:")
        print("   python launch_viper.py")
        print("   python start_trading.py")
        return 0
    else:
        print("\n❌ SYSTEM NOT READY - Please fix the issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())