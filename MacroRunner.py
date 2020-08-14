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
        runStart = time.time()

        currTime = time.time() - runStart
        pq = PriorityQueue()
        nextStep = 0
        scrolling = moving = False
        ticksPerScroll = 0
        ticksPerMove = (0, 0)
        scrollStartTime = moveStartTime = 0
        currScrollTick = 0
        currMoveTick = [0, 0]
        scrollDir = 0
        moveDir = (0, 0)

        while currTime < totalTime:
            # no more steps to perform
            if nextStep >= len(steps):
                print(currTime)
                currTime = time.time() - runStart
                time.sleep(.01)
                continue

            step = steps[nextStep]
            #print(step)
            stepType, data, holdTime, stepStart = step
            # check if ready to start next step
            if stepStart <= currTime:

                nextStep += 1
                #print((holdTime, stepType, data, stepStart))
                pq.put((holdTime, stepType, data, stepStart))
                # perform step
                if stepType == StepEnum.MOUSE_LEFT:
                    prev = mouse.position
                    mouse.position = data
                    mouse.press(Button.left)
                    mouse.position = prev
                        
                elif stepType == StepEnum.MOUSE_RIGHT:
                    prev = mouse.position
                    mouse.position = data
                    mouse.press(Button.right)
                    mouse.position = prev

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
                    xDir = distVec[0] / abs(distVec[0]) if distVec[0] != 0 else 0
                    yDir = distVec[1] / abs(distVec[1]) if distVec[1] != 0 else 0
                    moveDir = (xDir, yDir)
                    currMoveTick = [0, 0]

                elif stepType == StepEnum.KEY:
                    keyboard.press(data)

            # top denotes the step with the highest priority
            topHoldTime, topStepType, topData, topStart = \
                    pq.queue[0] if len(pq.queue) > 0 else (0, None, None, 0)

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
            if moving:
                xTickThreshold = ticksPerMove[0] * currMoveTick[0]
                yTickThreshold = ticksPerMove[1] * currMoveTick[1]
                xNumMove = (currMoveTime - xTickThreshold) // ticksPerMove[0]
                yNumMove = (currMoveTime - yTickThreshold) // ticksPerMove[1]

                if currMoveTime > xTickThreshold:
                    xMove = moveDir[0] * xNumMove
                    mouse.move(xMove, 0)
                    currMoveTick[0] += xNumMove
                if currMoveTime > yTickThreshold:
                    yMove = moveDir[1] * yNumMove
                    mouse.move(0, yMove)
                    currMoveTick[1] += yNumMove



            # if the time when the step was first performed plus the time 
            # the step was held for is less than the amount of time since
            # the macro started
            if topStepType != None and topStart + topHoldTime < currTime:
                # step is done so remove from queue
                pq.get(block=False)
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

            currTime = time.time() - runStart

            # sleep for cpu
            time.sleep(.01)
                            
