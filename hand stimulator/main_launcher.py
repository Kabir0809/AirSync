# Main launcher script for Hand Simulator Controller
# Allows user to choose between different controller implementations

import sys
import os

def show_menu():
    """Display controller options menu"""
    print("=" * 60)
    print("    HAND SIMULATOR GESTURE CONTROLLER")
    print("=" * 60)
    print()
    print("Choose your controller type:")
    print()
    print("1. Simple Controller - Basic hand gesture recognition")
    print("   - Easy to use, minimal setup")
    print("   - Basic finger and movement detection")
    print("   - Good for testing and beginners")
    print()
    print("2. Advanced Controller - Full featured with calibration")
    print("   - Complete gesture recognition system")
    print("   - Calibration for personalized control")
    print("   - Rotation detection and smoothing")
    print("   - Recommended for best experience")
    print()
    print("3. Hand Tracking Test - Test MediaPipe hand detection")
    print("   - Test hand detection accuracy")
    print("   - View landmark detection in real-time")
    print("   - Debug tool for troubleshooting")
    print()
    print("4. Key Input Test - Test keyboard simulation")
    print("   - Test key press functionality")
    print("   - Verify Hand Simulator key mappings")
    print("   - Useful for setup verification")
    print()
    print("0. Exit")
    print()
    print("=" * 60)

def run_controller(choice):
    """Run the selected controller"""
    try:
        if choice == '1':
            print("Starting Simple Hand Simulator Controller...")
            print("Make sure Hand Simulator is running and focused!")
            input("Press Enter to continue...")
            
            from simple_hand_simulator import SimpleHandSimulator
            controller = SimpleHandSimulator()
            controller.run()
            
        elif choice == '2':
            print("Starting Advanced Hand Simulator Controller...")
            print("This will start with a calibration process.")
            print("Make sure Hand Simulator is running and focused!")
            input("Press Enter to continue...")
            
            from advanced_hand_simulator import AdvancedHandSimulatorController
            controller = AdvancedHandSimulatorController()
            controller.run()
            
        elif choice == '3':
            print("Starting Hand Tracking Test...")
            
            from handtracking_simulator import HandSimulatorDetector
            detector = HandSimulatorDetector()
            
            # Run the main test function
            import handtracking_simulator
            handtracking_simulator.main()
            
        elif choice == '4':
            print("Starting Key Input Test...")
            
            from keyinput_simulator import test_keys
            test_keys()
            
        elif choice == '0':
            print("Goodbye!")
            sys.exit(0)
            
        else:
            print("Invalid choice! Please select 0-4.")
            return False
            
        return True
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Make sure all required files are present:")
        print("- simple_hand_simulator.py")
        print("- advanced_hand_simulator.py") 
        print("- handtracking_simulator.py")
        print("- keyinput_simulator.py")
        return False
        
    except Exception as e:
        print(f"Error running controller: {e}")
        print("Make sure you have:")
        print("- OpenCV installed (pip install opencv-python)")
        print("- MediaPipe installed (pip install mediapipe)")
        print("- NumPy installed (pip install numpy)")
        print("- A working webcam connected")
        return False

def check_requirements():
    """Check if required packages are installed"""
    required_packages = {
        'cv2': 'opencv-python',
        'mediapipe': 'mediapipe', 
        'numpy': 'numpy'
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"- {package}")
        print()
        print("Install missing packages with:")
        for package in missing_packages:
            print(f"pip install {package}")
        print()
        return False
    
    return True

def main():
    """Main launcher function"""
    print("Hand Simulator Controller Launcher")
    print("Checking requirements...")
    
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    print("All requirements satisfied!")
    print()
    
    while True:
        show_menu()
        
        try:
            choice = input("Select option (0-4): ").strip()
            
            if run_controller(choice):
                if choice != '0':
                    print()
                    print("Controller session ended.")
                    input("Press Enter to return to menu...")
                    print()
            else:
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()