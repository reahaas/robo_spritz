from direction_module import Direction_Module
from frame_module import Frame_Module

def main():
    frame_Module = Frame_Module()
    direction_module = Direction_Module(tolerance=10)
    for i in range(10):
        frame=frame_Module.get_frame()
        h,v=direction_module.get_direction(frame)
        print(f"{h=}  {v=}")

#Example usage
if __name__ == "__main__":
     main()
