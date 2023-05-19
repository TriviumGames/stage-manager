from pytimeparse.timeparse import timeparse
import re
import sys

def main():
    lines = sys.stdin.readlines()
    lost_time = 0.0
    line1 = lines.pop(0)
    line1_parts = line1.split(' ')
    duration = timeparse(line1_parts[4])
    frame_length = 1 / float(re.findall('\d*\.\d+|\d+', line1_parts[3])[0])
    codec = 'unknown'
    if line1_parts[1].find('hevc') != -1:
        codec = 'hevc'
    elif line1_parts[1].find('h264') != -1:
        codec = 'h264'
    #print(f"*******\n{line1_parts[0]:} (frame rate: {line1_parts[3]}, codec: {codec}")
    last_time = 0.0
    frames = 0
    lost_chunks = 0
    type = "AllThere"
    for line in lines:
        if line.strip() == 'EOF':
            if (last_time < duration):
                #print(f"Missing final frame {frames} @ {last_time} (missing {duration - last_time}s)")
                lost_time += duration - last_time
                lost_chunks += 1
                type = "Final"
            break
        else:
            frames += 1
            line_parts = list(filter(None, re.split('[ ~s]', line)))
           # print(line_parts)
            start_time = float(line_parts[0])
            if start_time > last_time:
                #print(f"Missing frame {frames} @ {last_time} (missing {start_time - last_time}s)")
                lost_time +=  start_time - last_time
                lost_chunks += 1
                type = "Penultimate"
            last_time = float(line_parts[1])

    #if (lost_time or lost_chunks):
    #    print(f"Found {frames} frames.  Missing {lost_time}s over {lost_chunks} segments (out of {duration}s total)")
    #else:
    #    print(f"All {frames} frames accounted for.  File is {duration}s long")
    print(f"{line1_parts[0]}, {codec}, {line1_parts[3]}, {frames}, {duration}, {type}")

if __name__ == '__main__':
    main()
