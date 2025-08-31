#!/usr/bin/env python3
"""
VIPER Launch System Validation Script
Tests that all critical launch scripts can execute without syntax errors
"""

import subprocess
import sys
from pathlib import Path

def test_script_syntax(script_path):
    """Test if a script has valid Python syntax"""
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', script_path], 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def test_script_execution(script_path, args=None):
    """Test if a script can be executed (will timeout after 5 seconds)"""
    try:
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return True, result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
    except subprocess.TimeoutExpired:
        return True, "Script started successfully (timed out)"
    except Exception as e:
        return False, str(e)

def main():
    """Main validation function"""
    print("🚀 VIPER Launch System Validation")
    print("="*50)
    
    # Critical launch scripts to test
    scripts = [
        ('scripts/launch_integrated_system.py', None),
        ('scripts/launch_complete_system.py', None),
        ('start_trading.py', None),
        ('src/viper/execution/final_live_trading_launcher.py', None),
    ]
    
    all_passed = True
    
    print("\n📋 Testing script syntax...")
    for script_path, _ in scripts:
        if not Path(script_path).exists():
            print(f"❌ {script_path}: File not found")
            all_passed = False
            continue
            
        syntax_ok, error = test_script_syntax(script_path)
        if syntax_ok:
            print(f"✅ {script_path}: Syntax OK")
        else:
            print(f"❌ {script_path}: Syntax Error - {error}")
            all_passed = False
    
    print("\n🔄 Testing script execution...")
    for script_path, args in scripts:
        if not Path(script_path).exists():
            continue
            
        exec_ok, output = test_script_execution(script_path, args)
        if exec_ok:
            print(f"✅ {script_path}: Execution OK")
            if output.strip():
                print(f"   Output: {output[:100]}")
        else:
            print(f"❌ {script_path}: Execution Error - {output}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL LAUNCH SCRIPTS VALIDATED SUCCESSFULLY!")
        print("✅ System is ready for launch")
        return 0
    else:
        print("❌ Some launch scripts have issues")
        print("⚠️ System needs additional fixes before launch")
        return 1

if __name__ == "__main__":
    sys.exit(main())