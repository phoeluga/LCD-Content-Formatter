import time
from dataclasses import dataclass
from RPLCD.i2c import CharLCD
import copy
import uuid

version = "1.0.2102.1401"

class HD44780(CharLCD):
    
    class Frame():
        @dataclass
        class FrameRow:
            id: str
            text: str
            prefix: str
            postfix: str

        def __init__(self):
            self.content = dict()
        
        def add(self, id, text = "", prefix = "", postfix=""):
            if self.content.get(id) is None:
                tr = self.FrameRow(id, text, prefix, postfix)
                self.content[id] = tr
                return tr
            else:
                raise ValueError("Object with ID '" + id + "' already exist in the frame!")
        def addWithGuid(self, text, prefix = "", postfix=""):
            id = uuid.uuid4()
            if self.content.get(id) is None:
                tr = self.FrameRow(id, text, prefix, postfix)
                self.content[id] = tr
                return tr
            else:
                raise ValueError("Object with ID '" + id + "' already exist in the frame!")
        def getFrame(self, id, createEmptyRowIfIdNotExist=True) -> FrameRow:
            fr = self.content.get(id)
            if fr is not None:
                return fr
            else:
                if createEmptyRowIfIdNotExist:
                    return self.add(id, "")
                raise ValueError("Object with ID '" + id + "' could not be found in frame!")
        def removeByIndex(self, id):
            if self.content.get(id) is not None:
                del self.content[id]
            else:
                raise NameError("Object with ID '" + id + "' could not be found in frame!")
        def clear(self):
            self.content.clear()
        def updateFrameRow(self, frameRow):
            if self.content.get(frameRow.id) is not None:
                self.content[frameRow.id] = frameRow
            else:
                raise ValueError("Object with ID '" + id + "' could not be found in frame!")
    
    def __init__(self, i2c_expander, address, cols, rows, dotsize=8, expander_params=None, port=1, charmap='A00', linebreaks=True, backlight=True):
        self._currentPageNumber = 1
        super().__init__(i2c_expander, address, expander_params, port, cols, rows, dotsize, charmap, linebreaks, backlight)
    
    def _getPagesCount(self, framebuffer) -> int:
        pagesCount = (int(len(framebuffer.content) / self.lcd.rows))
        if len(framebuffer.content) % self.lcd.rows != 0:
            pagesCount += 1
        return pagesCount
    
    def _getPaginationRange(self, framebuffer, pageNumber) -> range:
        pagesCount = self._getPagesCount(framebuffer)
        
        if pageNumber < pagesCount:
            rangeTo=self.lcd.rows*pageNumber
        else:
            rangeTo=len(framebuffer.content)

        paginationRange = range((self.lcd.rows*pageNumber) - self.lcd.rows, rangeTo)
        return paginationRange


    def writeFrame(self, framebuffer, pageNumber=1):
        if self._currentPageNumber != pageNumber:
            super().clear()
        self._currentPageNumber = pageNumber

        super().home()

        paginationRange = self._getPaginationRange(framebuffer, pageNumber)
        
        for i in paginationRange:
            text = list(framebuffer.content.values())[i].prefix + list(framebuffer.content.values())[i].text + list(framebuffer.content.values())[i].postfix
            super().write_string(text.ljust(self.lcd.cols)[:self.lcd.cols])
            super().write_string('\r\n')
        
        emptyRowsCount = self.lcd.rows - (paginationRange.stop - paginationRange.start)
        for j in range(emptyRowsCount):
            super().write_string(self.lcd.cols * ' ')
            super().write_string('\r\n')

    def scrollFrame(self, framebuffer, scrollIn=False, scrollToBlank=False, delay=0.5, showFirstFrameAfterScroll=True):
        @dataclass
        class TextPresentation:
            padding: str
            pos: int

        framebufferTmp = copy.deepcopy(framebuffer)
        textPresentations = []
        
        for row in framebuffer.content:
            if scrollIn:
                padding = ' ' * (self.lcd.cols - len(row.prefix))
            else:
                padding = ''
            textPresentations.append(TextPresentation(padding, 0))

        for pageNumber in range(1, (self._getPagesCount(framebuffer) + 1)):
            paginationRange = self._getPaginationRange(framebuffer, pageNumber)

            if scrollIn:
                if scrollToBlank:
                    maxIterations = max((len(list(framebuffer.content.values())[x].text) + len(list(framebuffer.content.values())[x].postfix) + 1 + (self.lcd.cols - len(list(framebuffer.content.values())[x].prefix))) for x in paginationRange)
                else:
                    maxIterations = max((len(list(framebuffer.content.values())[x].text) + len(list(framebuffer.content.values())[x].postfix) + 1) for x in paginationRange)
            else:
                if scrollToBlank:
                    maxIterations = max((len(list(framebuffer.content.values())[x].text) + len(list(framebuffer.content.values())[x].postfix) + 1) for x in paginationRange)
                else:
                    maxIterations = max((len(list(framebuffer.content.values())[x].text) + len(list(framebuffer.content.values())[x].postfix) + len(list(framebuffer.content.values())[x].prefix) - self.lcd.cols + 1) for x in paginationRange)

            if maxIterations <= 0:
                self.writeFrame(framebuffer, pageNumber)
                time.sleep(delay*2)
            else:
                for moveCount in range(maxIterations):
                    for frameRow in paginationRange:

                        if len(list(framebuffer.content.values())[frameRow].text) + len(list(framebuffer.content.values())[frameRow].postfix) + len(list(framebuffer.content.values())[frameRow].prefix) <= self.lcd.cols:
                            continue

                        if textPresentations[frameRow].pos >= len(textPresentations[frameRow].padding) + len(list(framebuffer.content.values())[frameRow].text) + len(list(framebuffer.content.values())[frameRow].postfix):
                            textPresentations[frameRow].pos = 0
                            list(framebufferTmp.content.values())[frameRow].text = copy.deepcopy(list(framebuffer.content.values())[frameRow])

                        text = textPresentations[frameRow].padding + list(framebuffer.content.values())[frameRow].text + textPresentations[frameRow].padding
                        pos = textPresentations[frameRow].pos
                        list(framebufferTmp.content.values())[frameRow].text = text[pos:pos+self.lcd.cols]
                        textPresentations[frameRow].pos += 1

                    self.writeFrame(framebufferTmp, pageNumber)
                    time.sleep(delay)

            if not scrollToBlank:
                time.sleep(delay*2)
                
        if showFirstFrameAfterScroll:
            self.writeFrame(framebuffer)