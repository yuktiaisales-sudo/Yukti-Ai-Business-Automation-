import pyautogui
import time

print("=" * 60)
print("MOUSE POSITION CALIBRATION")
print("=" * 60)

print()
print("You have 10 seconds.")
print("Move your mouse to the CENTER of the PUBLISH icon")
print("in Power BI Desktop.")
print()

for i in range(10, 0, -1):
    print(f"Move mouse... {i}")
    time.sleep(1)

x, y = pyautogui.position()

print()
print("=" * 60)
print("FINAL MOUSE POSITION")
print("=" * 60)
print(f"X = {x}")
print(f"Y = {y}")
print("=" * 60)

input("Press Enter to exit...")