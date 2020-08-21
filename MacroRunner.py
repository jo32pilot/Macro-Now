from StepConstants import StepEnum, keyConst
from pynput.keyboard import KeyCode
from pynput.mouse import Button
from queue import PriorityQueue
from threading import Thread
import time

class MacroRunner(Thread):

    # TODO this is stupid, refactor this
    def __init__(self, steps, totalTime, loopNum, mouse, keyboard, keys, recorder):
        args = (steps, totalTime, loopNum, mouse, keyboard, keys, recorder)
        super().__init__(target=self.runMacro, args=args)
        self.loopInf = True

    def _finishLoop(self):
        self.loopInf = False

    def runMacro(self, steps, totalTime, loopNum, mouse, keyboard, keys, recorder):
        # If -1, stop only when user re-presses hotkey
        resetHotkey = False

        recorder.backupHotkeys()
        if loopNum == -1:
            recorder.setMacroToggle(keys, self._finishLoop)
            resetHotkey = True
        else:
            self.loopInf = False

        loopTrack = loopNum

        while self.loopInf or loopTrack >= 0:
            loopTrack -= 1
            runStart = time.time()

            currTime = time.time() - runStart
            pq = PriorityQueue()
            nextStep = 0
            scrolling = False
            ticksPerScroll = 0
            scrollStartTime = 0
            currScrollTick = 0
            scrollDir = 0

            while currTime < totalTime:

                # more steps to perform
                if nextStep < len(steps):
                    step = steps[nextStep]
                    stepType, data, holdTime, stepStart = step
                    # check if ready to start next step
                    if stepStart <= currTime:

                        nextStep += 1
                        pq.put((holdTime, stepType, data, stepStart))

                        # perform step. no case for mouse move because we'll
                        # just move the mouse to the end at the end of the hold time.
                        # ran into problems when trying to simplify mouse movement
                        # into a straight line and moving gradually. Maybe can 
                        # save all points in mouse movement but sounds horribly
                        # ineffecient
                        if stepType == StepEnum.MOUSE_LEFT:
                            mouse.position = data
                            mouse.press(Button.left)
                                
                        elif stepType == StepEnum.MOUSE_RIGHT:
                            mouse.position = data
                            mouse.press(Button.right)

                        elif stepType == StepEnum.MOUSE_SCROLL:
                            ticksPerScroll = abs(holdTime / data) if data != 0 else 0
                            scrolling = True
                            scrollStartTime = time.time()
                            scrollDir = 1 if data > 0 else -1
                            mouse.scroll(0, scrollDir)
                            currScrollTick = 1

                        elif stepType == StepEnum.MOUSE_MOVE:
                            start, end = data
                            x, y = start
                            mouse.position = (int(x), int(y))

                        elif stepType == StepEnum.KEY:
                            key = data if len(data) == 1 else keyConst(data)
                            keyboard.press(key)

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
                        start, end = topData
                        x, y = end
                        mouse.position = (int(x), int(y))
                    elif topStepType == StepEnum.KEY:
                        key = topData if len(topData) == 1 else keyConst(topData)
                        keyboard.release(key)

                currTime = time.time() - runStart

                # sleep for cpu
                time.sleep(.01)

        if resetHotkey:
            idx = recorder.findHotkey(keys, recording=False)
            recorder.setHotkey(idx, keys, steps, totalTime, loopNum, recording=False)
        recorder.reloadHotkeys()
        hk = recorder.mapper._hotkeys[0]
        print(f'hotkey: {hk._keys} func: {hk._on_activate}')

