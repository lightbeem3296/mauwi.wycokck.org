import shutil


total = 26000
number = 20
step = total // number + 1
for i in range(number):
    start = step * i
    shutil.copyfile("sel_0_100.py", f"sel_{start}_{step}.py")
