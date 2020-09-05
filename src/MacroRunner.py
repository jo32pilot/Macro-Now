"""File containing the class the run a macro.

This file needs major refactoring.
"""

import pynput._util.win32_vks as VK
from StepConstants import StepEnum, keyConst, keyToVK, isVKPress
from StepEvents import KeyboardEvent
from KeyboardController import pressKey, releaseKey
from pynput.keyboard import KeyCode
from win32api import MapVirtualKey, VkKeyScan
from pynput.mouse import Button
from queue import PriorityQueue
from threading import Thread
import time

class MacroRunner(Thread):

    _DELTA = .1

    # TODO this is stupid, refactor this
    def __init__(self, steps, totalTime, loopNum, mouse, keyboard, keys,
            recorder):
        args = (steps, totalTime, loopNum, mouse, keyboard, keys, recorder)
        super().__init__(target=self.runMacro, args=args)
        self.loopInf = True

    def _finishLoop(self):
        self.loopInf = False

    def runMacro(self, steps, totalTime, loopNum, mouse, keyboard, keys,
            recorder):

        # If -1, stop only when user re-presses hotkey
        resetHotkey = False

        recorder.backupHotkeys()
        if loopNum == -1:
            recorder.setMacroToggle(keys, self._finishLoop)
            resetHotkey = True
        else:
            self.loopInf = False

        loopTrack = loopNum

        while self.loopInf or loopTrack > 0:
            loopTrack -= 1
            runStart = time.time()

            keySet = set()
            currTime = time.time() - runStart
            pq = PriorityQueue()
            nextStep = 0
            scrolling = False
            ticksPerScroll = 0
            scrollStartTime = 0
            currScrollTick = 0
            scrollDir = 0

            while currTime < totalTime + MacroRunner._DELTA:


                # more steps to perform
                if nextStep < len(steps):
                    step = steps[nextStep]
                    stepType, data, holdTime, stepStart = step
                    # check if ready to start next step
                    if stepStart <= currTime:

                        isKeyTap = stepType == StepEnum.KEY and holdTime == 0
                        nextStep += 1
                        if not isKeyTap:
                            pq.put((holdTime, stepType, data, stepStart))

                        # perform step.
                        if stepType == StepEnum.MOUSE_LEFT:
                            mouse.position = data
                            mouse.press(Button.left)
                                
                        elif stepType == StepEnum.MOUSE_RIGHT:
                            mouse.position = data
                            mouse.press(Button.right)

                        elif stepType == StepEnum.MOUSE_SCROLL:
                            ticksPerScroll = abs(holdTime / data) if data != 0 \
                                    else 0
                            scrolling = True
                            scrollStartTime = time.time()
                            scrollDir = 1 if data > 0 else -1
                            mouse.scroll(0, scrollDir)
                            currScrollTick = 1

                        elif stepType == StepEnum.MOUSE_LEFT_DRAG:
                            x, y = data[0]
                            mouse.position = (int(x), int(y))
                            mouse.press(Button.left)
                            print('pressed')

                        elif stepType == StepEnum.MOUSE_RIGHT_DRAG:
                            x, y = data[0]
                            mouse.position = (int(x), int(y))
                            mouse.press(Button.right)

                        elif stepType == StepEnum.KEY:
                            key = VkKeyScan(data) if len(data) == 1 \
                                    else keyConst(data)
                            scanKey = MapVirtualKey(keyToVK(key), 0)
                            if isVKPress(key):
                                keyboard.press(key)
                            elif isKeyTap:
                                pressKey(scanKey)
                                releaseKey(scanKey)
                            else:
                                keySet.add(scanKey)
                                pressKey(scanKey)
                                releaseKey(scanKey)

                # top denotes the step with the highest priority
                topHoldTime, topStepType, topData, topStart = \
                        pq.queue[0] if len(pq.queue) > 0 else (0, None, None, 0)

                currScrollTime = time.time() - scrollStartTime
                currTickThreshold = ticksPerScroll * currScrollTick

                # if scrolling performed and current amount of time spent
                # scrolling exceeds the current threshold to scroll again
                if scrolling and currScrollTime > currTickThreshold:

                    # If currScrollTime > ticksPerMove * (currMoveTick + 1),
                    # then we won't reach the end point by the end time (this
                    # could occur because we've slept for too long). So we
                    # perform the following calculation (same idea for move)
                    scrollDiff = currScrollTime - currTickThreshold
                    numScroll = (scrollDiff) // ticksPerScroll

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

                    elif topStepType == StepEnum.MOUSE_LEFT_DRAG:
                        start, end = topData
                        x, y = end
                        mouse.position = (int(x), int(y))
                        mouse.release(Button.left)
                    elif topStepType == StepEnum.MOUSE_RIGHT_DRAG:
                        start, end = topData
                        x, y = end
                        mouse.position = (int(x), int(y))
                        mouse.release(Button.right)

                    elif topStepType == StepEnum.KEY:
                        key = VkKeyScan(topData) if len(topData) == 1 \
                                else keyConst(topData)
                        if isVKPress(key):
                            keyboard.release(key)
                        else:
                            key = MapVirtualKey(keyToVK(key), 0)
                            try:
                                keySet.remove(key)
                            except KeyError:
                                print(key)

                for key in keySet:
                    pressKey(key)
                    releaseKey(key)

                currTime = time.time() - runStart

                # sleep for cpu
                time.sleep(.02)

        if resetHotkey:
            idx = recorder.findHotkey(keys, recording=False)
            recorder.setHotkey(idx, keys, steps, totalTime, loopNum,
                    recording=False)
        recorder.reloadHotkeys()

