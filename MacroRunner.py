from StepConstants import StepEnum
from pynput.mouse import Button
from queue import PriorityQueue
from threading import Thread
import time

class MacroRunner(Thread):
    def __init__(self, steps, totalTime, mouse, keyboard):
        args = (steps, totalTime, mouse, keyboard)
        super().__init__(target=self.runMacro, args=args)

    def runMacro(self, steps, totalTime, mouse, keyboard):
        start = time.time()

        currTime = time.time() - start
        pq = PriorityQueue()
        nextStep = 0
        scrolling = moving = False
        ticksPerScroll = ticksPerMove = 0
        currScrollTick = currMoveTick = 0
        scrollStartTime = moveStartTime = 0
        scrollDir = 0
        moveDir = (0, 0)

        while currTime < totalTime:

            step = steps[nextStep]
            stepType, data, holdTime, stepStart = step

            # check if ready to start next step
            if stepStart >= currTime:

                nextStep += 1
                pq.put((holdTime, stepType, data, stepStart))

                # perform step
                if stepType == StepEnum.MOUSE_LEFT:
                    mouse.press(Button.left)
                        
                elif stepType == StepEnum.MOUSE_RIGHT:
                    mouse.press(Button.right)

                elif stepType == StepEnum.MOUSE_SCROLL:
                    ticksPerScroll = abs(holdTime / data)
                    scrolling = True
                    scrollStartTime = time.time()
                    scrollDir = 1 if data > 0 else -1
                    mouse.scroll(0, scrollDir)
                    # TODO maybe shouldn't initialize to 1? might go 1 too far 
                    # or too early
                    currScrollTick = 1

                elif stepType == StepEnum.MOUSE_MOVE:
                    start, end = data
                    mouse.position = start

                    # vector in direction from start to end
                    distVec = (end[0] - start[0], end[1] - start[1])

                    ticksPerMove = (holdTime / distVec[0], 
                            holdTime / distVec[1])
                    moving = True
                    moveStartTime = time.time()
                    xDir = distVec[0] / abs(distVec[0])
                    yDir = distVec[1] / abs(distVec[1])
                    moveDir = (xDir, yDir)
                    mouse.move(xDir, yDir)
                    currMoveTick = 1

                elif stepType == StepEnum.KEY:
                    keyboard.press(data)

            # top denotes the step with the highest priority
            topHoldTime, topStepType, topData, topStart = pq.queue[0]

            currScrollTime = time.time() - scrollStartTime
            currTickThreshold = ticksPerScroll * currScrollTick

            # if scrolling performed and current amount of time spent scrolling
            # exceeds the current threshold to scroll again
            if scrolling and currScrollTime > currTickThreshold:

                # If currScrollTime > ticksPerMove * (currMoveTick + 1),
                # then we won't reach the end point by the end time (this could
                # occur because we've slept for too long). So we perform the
                # following calculation (same idea for move)
                numScroll = (currScrollTime - currTickThreshold) // ticksPerScroll

                yScroll = scrollDir * numScroll
                mouse.scroll(0, yScroll)
                currScrollTick += numScroll

            
            currMoveTime = time.time() - moveStartTime
            currTickThreshold = ticksPerMove * currMoveTick
            if moving and currMoveTime > currTickThreshold:
                #TODO, seperate into two if cases, 1 for x, 1 for y
                numMove = (currMoveTime - currTickThreshold) // ticksPerMove
                xMove = moveDir[0] * numMove
                yMove = moveDir[1] * numMove
                mouse.move(xMove, yMove)
                currScrollTick += numMove


            # if the time when the step was first performed plus the time 
            # the step was held for is less than the amount of time since
            # the macro started
            if topStart + topHoldTime < currTime:

                # step is done so remove from queue
                pq.get()
                    
                # unperform step
                if topStepType == StepEnum.MOUSE_LEFT:
                    mouse.release(Button.left)
                elif topStepType == StepEnum.MOUSE_RIGHT:
                    mouse.release(Button.right)
                elif topStepType == StepEnum.MOUSE_SCROLL:
                    # only need to set scrolling to False because
                    # next time scrolling is set to True, all other
                    # relavent variables will be set to new values
                    scrolling = False
                elif topStepType == StepEnum.MOUSE_MOVE:
                    # only need to set moving to False because
                    # next time moving is set to True, all other
                    # relavent variables will be set to new values
                    moving = False
                elif topStepType == StepEnum.KEY:
                    keyboard.release(topData)



            currTime = time.time() - start

            # sleep for cpu
            time.sleep(.01)

                    
